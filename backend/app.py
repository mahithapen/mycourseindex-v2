from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
import json
from canvas import scrape_canvas_courses
from ed import main
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

s3 = boto3.client('s3')

bedrock_client = boto3.client('bedrock', region_name='us-east-1')  

S3_BUCKET_NAME = 'your-bucket-name' ##CHANGE THIS!!!

@app.route('/scrape_and_upload', methods=['POST'])
def scrape_and_upload():
    token = request.json.get('token')
    course_ids = request.json.get('course_ids', 'all')
    ed_host = request.json.get('ed_host')
    ed_token = request.json.get('ed_token')

    if not token:
        return jsonify({'error': 'Canvas API token is required.'}), 400
    #we might need to fix ed.py to be integrated with the s3 bucket upload
    if ed_host and ed_token:
        try:
            all_ed_course_data = main(ed_host, ed_token)

            for course_id, course_data in all_ed_course_data.items():
                s3_key = f'courses/{course_id}_ed.json'
                course_json = json.dumps(course_data)
                s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=course_json)
                print(f"Uploaded ED course {course_id} data to S3.")
        except Exception as e:
            return jsonify({'error': f"ED scraping failed: {str(e)}"}), 500
    else:
        print("ED host or token not provided. Skipping ED scraping.")

    #canvas:
    try:
        all_course_data = scrape_canvas_courses(token, course_ids)

        for course_id, course_data in all_course_data.items():
            s3_key = f'courses/{course_id}.json'
            course_json = json.dumps(course_data)
            s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=course_json)
            print(f"Uploaded course {course_id} data to S3.")

        return jsonify({'message': 'Scraping and uploading completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
 


#this queries s3 bucket and calls bedrock - we might not need this because lambda functions can call the bedrock after.
@app.route('/query', methods=['POST'])
def query():
    course_id = request.json.get('course_id')
    query_text = request.json.get('query')

    if not course_id or not query_text:
        return jsonify({'error': 'course_id and query are required fields.'}), 400

    try:
        s3_response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=f'courses/{course_id}.json')
        course_content = json.loads(s3_response['Body'].read().decode('utf-8'))

        response = llm_call(query_text, course_content)
        return jsonify({'response': response})

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return jsonify({'error': f'Course content for course_id {course_id} not found.'}), 404
        else:
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#bedrock call
def llm_call(query_text, course_content):
    context_pieces = []
    max_context_length = 5000  

    for item in course_content:
        content = ''
        if 'content' in item:
            content = item['content']
        elif 'body' in item:
            content = item['body']
        elif 'file_name' in item and 'content' in item:
            content = f"{item['file_name']}:\n{item['content']}"

        if len(' '.join(context_pieces + [content]).split()) <= max_context_length:
            context_pieces.append(content)
        else:
            break

    context = "\n\n".join(context_pieces)
    #CLAUDE PART:
    prompt = f"{context}\n\nQuestion: {query_text}\nAnswer:"

    payload = {
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.7,
        "stop_sequences": ["\n\n"],
        "top_k": 250,
        "top_p": 1.0
    }

    response = bedrock_client.invoke_model(
        modelId='anthropic.claude-v2',  
        contentType='application/json',
        accept='application/json',
        body=json.dumps(payload).encode('utf-8')
    )

    response_body = response['body'].read().decode('utf-8')
    response_json = json.loads(response_body)
    answer = response_json.get('completion', '').strip()

    return answer
#need function for call to push items to s3
if __name__ == '__main__':
    app.run(debug=True)
