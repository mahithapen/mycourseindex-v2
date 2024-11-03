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
