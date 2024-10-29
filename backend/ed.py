# # #!/usr/bin/env python3

# # import sys
# # import time
# # import requests

# # def request(method, url, **kwargs):
# #     status = ''
# #     body = ''

# #     try:
# #         r = requests.request(method, url, **kwargs)
# #         status = r.status_code
# #         body = r.text

# #         if 200 <= r.status_code <= 299:
# #             return r
# #         else:
# #             raise Exception('Bad status code: ', status)

# #     except Exception as e:
# #         print('Request failed')
# #         print(f'Status: {status}')
# #         print(f'URL: {url}')
# #         print(f'Body: {body}')
# #         status = str(e);

# #         raise e

# # def main():
# #     ed_host, token = sys.argv[1:]

# #     r = request('GET', ed_host + '/user', headers={'Authorization': 'Bearer ' + token})
# #     u = r.json()

# #     print('Logged in as', u['user']['email'])

# # if __name__ == '__main__':
# #     main()



# #!/usr/bin/env python3

# import sys
# import requests

# def request(method, url, **kwargs):
#     try:
#         r = requests.request(method, url, **kwargs)
#         r.raise_for_status()  # Raises HTTPError for bad status codes
#         return r
#     except requests.exceptions.RequestException as e:
#         print(f'Request failed: {e}')
#         raise e

# def get_courses(ed_host, token):
#     # Fetch user data, which includes courses
#     r = request('GET', f'{ed_host}/user', headers={'Authorization': f'Bearer {token}'})
#     return r.json()['courses']  # Return the courses

# # def get_discussions(ed_host, course_id, token):
# #     # Fetch discussions for a specific course (adjusting URL to the correct format)
# #     r = request('GET', f'{ed_host}/courses/{course_id}/discussion', 
# #                 headers={'Authorization': f'Bearer {token}'})
# #     return r.json()

# def get_discussions(ed_host, course_id, token):
#     # Construct the correct discussions endpoint
#     url = f'{ed_host}/courses/{course_id}/discussion'  # Adjusted to plural
#     print(f"Fetching discussions from URL: {url}")  # Debug line
#     r = request('GET', url, headers={'Authorization': f'Bearer {token}'})
#     return r.json()

# def get_discussion_content(ed_host, course_id, discussion_id, token):
#     # Fetch a specific discussion's content (adjusting URL to the correct format)
#     r = request('GET', f'{ed_host}/courses/{course_id}/discussion/{discussion_id}', 
#                 headers={'Authorization': f'Bearer {token}'})
#     return r.json()

# def main():
#     # Expecting only the API base URL and token as arguments
#     ed_host, token = sys.argv[1:]

#     # Step 1: Get all courses the user is enrolled in
#     courses = get_courses(ed_host, token)
    
#     for course in courses:
#         course_id = course['course']['id']
#         course_name = course['course']['name']
#         print(f"\n--- Fetching discussions for course: {course_name} (ID: {course_id}) ---\n")

#         # Step 2: Get all discussions in the course
#         discussions = get_discussions(ed_host, course_id, token)

#         # Step 3: Loop through all discussions and print content
#         for discussion in discussions:
#             discussion_id = discussion['id']
#             discussion_title = discussion['title']

#             print(f"Discussion Title: {discussion_title} (ID: {discussion_id})")

#             # Get the content of the discussion
#             discussion_data = get_discussion_content(ed_host, course_id, discussion_id, token)
            
#             # Assuming 'body' contains the question and 'replies' contain answers
#             print(f"Question: {discussion_data['body']}\n")

#             # If there are replies or answers
#             if 'replies' in discussion_data:
#                 for reply in discussion_data['replies']:
#                     user_name = reply['user']['name']
#                     print(f"Reply by {user_name}: {reply['body']}")
#             print("\n" + "="*50 + "\n")





import sys
import requests
import json
import time
from random import uniform

class RateLimitException(Exception):
    """Custom exception for rate limit errors"""
    pass

def exponential_backoff(attempt, max_attempts=5, base_delay=1):
    """Calculate delay with exponential backoff and jitter."""
    if attempt >= max_attempts:
        raise RateLimitException(f"Max retry attempts ({max_attempts}) exceeded")
    
    delay = min(300, base_delay * (2 ** attempt))  # Cap at 5 minutes
    jitter = uniform(0, 0.1 * delay)  # Add 0-10% jitter
    return delay + jitter

def request(method, url, max_attempts=5, **kwargs):
    """Make an HTTP request with exponential backoff retry logic."""
    attempt = 0
    while True:
        try:
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 429:  # Rate limit hit
                if attempt >= max_attempts:
                    raise RateLimitException(f"Rate limit exceeded after {max_attempts} attempts")
                
                delay = exponential_backoff(attempt, max_attempts)
                print(f"Rate limit hit. Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
                attempt += 1
                continue
                
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            # Only print response details if response has been defined
            if 'response' in locals() and response.status_code == 429:
                continue  # Try again with exponential backoff
            print(f'Request failed: {e}')
            raise e


def get_courses(ed_host, token):
    """Fetch all courses for the authenticated user."""
    r = request('GET', 
                f'{ed_host}/user', 
                headers={'Authorization': f'Bearer {token}'})
    return r.json().get('courses', [])

def get_thread_content(ed_host, thread_id, token):
    """Fetch detailed content for a specific thread with rate limit handling."""
    try:
        r = request('GET', 
                    f'{ed_host}/threads/{thread_id}?view=1',
                    headers={'Authorization': f'Bearer {token}'})
        return r.json()
    except RateLimitException as e:
        print(f"Rate limit hit while fetching thread {thread_id}: {e}")
        print("Waiting 60 seconds before continuing...")
        time.sleep(60)
        return {"thread": {"answers": []}, "users": []}

def get_threads(ed_host, course_id, token):
    """Fetch all threads for a specific course using offset-based pagination."""
    threads = []
    offset = 0
    limit = 10  # Reduced from 20 to be more conservative
    consecutive_empty_responses = 0
    max_empty_responses = 3
    
    while True:
        try:
            print(f"\nFetching threads with offset {offset}...")
            url = f'{ed_host}/courses/{course_id}/threads'
            print(f"URL: {url}")
            print(f"Parameters: offset={offset}, limit={limit}")
            
            r = request('GET', 
                       url,
                       params={'offset': offset, 'limit': limit},
                       headers={'Authorization': f'Bearer {token}'})
            
            data = r.json()
            new_threads = data.get('threads', [])
            
            print(f"Number of threads in response: {len(new_threads)}")
            
            if not new_threads:
                consecutive_empty_responses += 1
                print(f"No threads found at offset {offset}")
                if consecutive_empty_responses >= max_empty_responses:
                    print(f"Stopping after {max_empty_responses} consecutive empty responses")
                    break
            else:
                consecutive_empty_responses = 0
                threads.extend(new_threads)
                print(f"\nFetched {len(new_threads)} threads")
                print(f"Total threads so far: {len(threads)}")
            
            offset += limit
            
            # Increased base delay between requests
            time.sleep(uniform(1.0, 2.0))
            
        except RateLimitException as e:
            print(f"Rate limit hit while fetching thread list: {e}")
            print("Waiting 60 seconds before continuing...")
            time.sleep(60)
            continue
            
        except Exception as e:
            print(f"Unexpected error at offset {offset}: {e}")
            break
    
    print(f"\nFinal summary:")
    print(f"Successfully fetched total of {len(threads)} threads for course ID {course_id}")
    return threads

def main():
    """Main function to orchestrate the data collection process."""
    if len(sys.argv) != 3:
        print("Usage: python script.py <ed_host> <token>")
        sys.exit(1)
        
    ed_host, token = sys.argv[1:]
    class_qna_dict = {}

    try:
        courses = get_courses(ed_host, token)
        
        for course in courses:
            course_id = course['course']['id']
            course_name = course['course']['name']
            print(f"\n--- Fetching threads for course: {course_name} (ID: {course_id}) ---\n")

            class_qna_dict[course_name] = []
            
            try:
                threads = get_threads(ed_host, course_id, token)

                for thread in threads:
                    thread_id = thread['id']
                    title = thread.get('title', 'No title')
                    body = thread.get('document', 'No question text')

                    question_text = title if body.strip() in {"^", "title", "Title", "TITLE"} or "title" in body.strip().lower() else body

                    try:
                        thread_data = get_thread_content(ed_host, thread_id, token)
                        answers = thread_data['thread'].get('answers', [])
                        users = {user['id']: user['name'] for user in thread_data.get('users', [])}

                        answer_texts = []
                        if answers:
                            for answer in answers:
                                answer_content = answer.get('document', 'No answer text')
                                answer_texts.append(answer_content)
                        else:
                            answer_texts = ["No answers available"]

                        answer_data = answer_texts if len(answer_texts) > 1 else answer_texts[0]
                        class_qna_dict[course_name].append((question_text, answer_data))
                        
                    except RateLimitException:
                        print(f"Skipping thread {thread_id} due to rate limiting")
                        continue

            except RateLimitException:
                print(f"Skipping remaining threads for course {course_name} due to rate limiting")
                continue

        # Write dictionary to JSON file
        with open('class_qna_data.json', 'w', encoding='utf-8') as f:
            json.dump(class_qna_dict, f, ensure_ascii=False, indent=4)

        print("Data successfully written to class_qna_data.json")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
