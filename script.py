from locust import HttpUser, task, between, events
from bs4 import BeautifulSoup
import random

class DirectSSOLoadTest(HttpUser):
    wait_time = between(0, 0.1)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = [
            {"username": "zico2eco@gmail.com", "password": "test123"},
        ]

    @task
    def direct_sso_test(self):
        """Test direct SSO access and dashboard redirect"""
        current_user = random.choice(self.users)
        
        try:
            # Get SSO login page and CSRF token
            with self.client.get("/sso/login", name="get_sso_page", catch_response=True) as sso_response:
                if sso_response.status_code != 200:
                    sso_response.failure("Failed to get SSO page")
                    return
                
                soup = BeautifulSoup(sso_response.text, 'html.parser')
                csrf_element = soup.find('input', {'name': '_csrf'})
                sso_csrf = csrf_element['value'] if csrf_element else None
                
                if not sso_csrf:
                    sso_response.failure("Could not find CSRF token")
                    return

            # Attempt login
            login_data = {
                'username': current_user['username'],
                'password': current_user['password'],
                '_csrf': sso_csrf
            }
            
            with self.client.post(
                "/sso/login",
                data=login_data,
                name="direct_sso_login",
                catch_response=True,
                allow_redirects=False  # Don't follow redirects yet
            ) as login_response:
                #print("Login Status Code:", login_response.status_code)
                #print("Login Headers:", login_response.headers)
                
                if login_response.status_code == 302:  # Redirect
                    redirect_url = login_response.headers.get('Location', '')
                    #print("Redirect URL:", redirect_url)
                    
                    # Check if redirected back to login page with error
                    if 'error' in redirect_url or 'login?error' in redirect_url:
                        login_response.failure("Login failed - Invalid credentials")
                        return
                    
                    # Follow the redirect manually
                    with self.client.get(
                        redirect_url,
                        name="follow_redirect",
                        catch_response=True
                    ) as redirect_response:
                        if redirect_response.status_code != 200:
                            login_response.failure(f"Redirect failed with status {redirect_response.status_code}")
                            return

                elif login_response.status_code != 200:
                    login_response.failure(f"Login failed with status {login_response.status_code}")
                    return

                # If we got here, login was successful
                login_response.success()
                
                # Now check dashboard access
                with self.client.get(
                    "/sso/dashboard",
                    name="check_dashboard_access",
                    catch_response=True
                ) as dashboard_response:
                    #print("Dashboard Status Code:", dashboard_response.status_code)
                    if dashboard_response.status_code == 200:
                        # Verify we got actual dashboard content, not login page
                        if "login" in dashboard_response.text.lower():
                            dashboard_response.failure("Redirected to login page - Not authenticated")
                        else:
                            dashboard_response.success()
                    else:
                        dashboard_response.failure(f"Dashboard access failed with status {dashboard_response.status_code}")

        except Exception as e:
            print(f"Test failed for user {current_user['username']}: {str(e)}")

# Event handlers for monitoring
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    if name == "direct_sso_login" and exception is None:
        print(f"Login attempt - Response time: {response_time}ms")
    elif name == "check_dashboard_access" and exception is None:
        print(f"Dashboard access attempt - Response time: {response_time}ms")
