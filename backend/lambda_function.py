import json
import boto3

def lambda_handler(event, context):
    # Initialize Bedrock client
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Test course materials
    s3 = boto3.client('s3')
    bucket_name = "course-materials-storage"
    prefix = "courses/course-101/"
    data = ""
    
    # List of objects in S3 bucket
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    # Check if there are any contents
    if 'Contents' in response:
        files = [obj['Key'] for obj in response['Contents']]
        data = json.dumps({'files': files})
        print(data)
    
    # Set model ID
    model_id = "us.meta.llama3-2-1b-instruct-v1:0"

    # Prepare Bedrock payload
    payload = {
        "prompt": f"Analyze the following information:\n\n{data}Could someone please explain why there cannot be current in the top wire?"
    }

    try:
        # Invoke model using Bedrock API
        response = bedrock.invoke_model(
            modelId = model_id,
            contentType = "application/json",
            accept = "application/json",
            body = json.dumps(payload)
        )

        # Process Bedrock's response: decode StreamingBody as JSON
        response_body = response['body'].read().decode('utf-8')
        result = json.loads(response_body)

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        print(f"Error invoking Bedrock: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
