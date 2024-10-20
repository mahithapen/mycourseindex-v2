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





#!/usr/bin/env python3

import sys
import requests

def request(method, url, **kwargs):
    try:
        r = requests.request(method, url, **kwargs)
        r.raise_for_status()  # Raises HTTPError for bad status codes
        return r
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
        raise e

def get_courses(ed_host, token):
    # Fetch user data, which includes courses
    r = request('GET', f'{ed_host}/user', headers={'Authorization': f'Bearer {token}'})
    return r.json()['courses']  # Return the courses

def get_threads(ed_host, course_id, token):
    # Fetch threads for a specific course
    url = f'{ed_host}/courses/{course_id}/threads'  # Adjusted endpoint for threads
    print(f"Fetching threads from URL: {url}")  # Debug line
    r = request('GET', url, headers={'Authorization': f'Bearer {token}'})

    # Debug print the response to see its structure
    print(f"Threads response: {r.json()}")  # Debug line

    return r.json()  # Return the list of threads

def get_thread_content(ed_host, thread_id, token):
    # Fetch a specific thread's content
    r = request('GET', f'{ed_host}/threads/{thread_id}?view=1', 
                headers={'Authorization': f'Bearer {token}'})
    return r.json()  # Return the thread content

def main():
    # Expecting only the API base URL and token as arguments
    ed_host, token = sys.argv[1:]

    # Step 1: Get all courses the user is enrolled in
    courses = get_courses(ed_host, token)
    
    for course in courses:
        course_id = course['course']['id']
        course_name = course['course']['name']
        print(f"\n--- Fetching threads for course: {course_name} (ID: {course_id}) ---\n")

        # Step 2: Get all threads in the course
        threads = get_threads(ed_host, course_id, token)

        # Step 3: Loop through all threads and print content
        for thread in threads:
            thread_id = thread['id']
            thread_title = thread['title']

            print(f"Thread Title: {thread_title} (ID: {thread_id})")

            # Get the content of the thread
            thread_data = get_thread_content(ed_host, thread_id, token)
            
            # Assuming 'body' contains the question and 'replies' contain answers
            print(f"Question: {thread_data['body']}\n")

            # If there are replies or answers
            if 'replies' in thread_data:
                for reply in thread_data['replies']:
                    user_name = reply['user']['name']
                    print(f"Reply by {user_name}: {reply['body']}")
            print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
