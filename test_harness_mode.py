#!/usr/bin/env python
"""
API Endpoint Tester for Split API Client

This script tests both Harness mode and standard Split API endpoints.
It requires the user to provide their account_identifier and API keys.
"""

import sys
import json
import time
import logging
import signal
from pprint import pprint
from splitapiclient.main import get_client
from splitapiclient.util.exceptions import HTTPResponseError

# Set up logging
logger = logging.getLogger('test_harness_endpoints')
logger.setLevel(logging.DEBUG)  # Set to DEBUG to see detailed logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def print_separator(title=None):
    """Print a separator line with an optional title."""
    width = 80
    if title:
        print(f"\n{'=' * 10} {title} {'=' * (width - len(title) - 12)}")
    else:
        print(f"\n{'=' * width}")

def print_result(title, result, error=None):
    """Print the result of an API call."""
    print_separator(title)
    if error:
        print(f"ERROR: {error}")
        logger.error(f"{title} failed: {error}")
        return False
    else:
        if isinstance(result, list):
            print(f"Found {len(result)} items")
            logger.info(f"{title}: Found {len(result)} items")
            if len(result) > 0:
                try:
                    # Try to get the first item's attributes
                    if hasattr(result[0], '__dict__'):
                        pprint(vars(result[0]))
                    else:
                        pprint(result[0])
                except (IndexError, TypeError):
                    print("Could not display first item")
        elif result is True:
            print("Operation completed successfully")
            logger.info(f"{title}: Operation completed successfully")
        else:
            try:
                if hasattr(result, '__dict__'):
                    pprint(vars(result))
                else:
                    pprint(result)
            except (AttributeError, TypeError):
                print(f"Result: {result}")
                logger.info(f"{title}: {result}")
        return True

def safe_api_call(func, *args, timeout=30, **kwargs):
    """Safely call an API function and handle exceptions."""
    try:
        logger.info(f"Calling {func.__qualname__} with args: {args}, kwargs: {kwargs}")
        # We can't pass timeout directly to the microclient methods
        # Instead, we need to find a way to set the timeout on the underlying HTTP client
        # For now, we'll just remove the timeout parameter
        result = func(*args, **kwargs)
        return result, None
    except HTTPResponseError as e:
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            try:
                error_details = json.loads(e.response.text)
                logger.error(f"HTTP Response Error: {e}, Details: {error_details}")
                return None, f"{error_details}"
            except (json.JSONDecodeError, AttributeError):
                error_text = e.response.text if hasattr(e.response, 'text') else 'No details'
                logger.error(f"HTTP Response Error: {e}, Text: {error_text}")
                return None, f"{e} - {error_text}"
        logger.error(f"HTTP Response Error: {e}")
        return None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return None, str(e)

def get_resource_identifier(resource):
    """
    Get the identifier of a resource, trying different attribute names.
    
    Different resource types might use different attribute names for their identifiers.
    This function tries common attribute names and returns the first one found.
    """
    for attr in ['_identifier', '_id', 'id', '_uuid', 'uuid', 'name', '_name']:
        if hasattr(resource, attr):
            return getattr(resource, attr)
    
    # If no identifier attribute is found, convert the resource to a string
    # This is a fallback and might not work for all resources
    return str(resource)

def test_token_endpoints(client, account_id):
    """Test token-related endpoints."""
    print_separator("TESTING TOKEN ENDPOINTS")
    logger.info("Starting token endpoint tests")
    
    try:
        # List tokens
        result, error = safe_api_call(client.token.list, account_id)
        success = print_result("List Tokens", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific token
            token_id = get_resource_identifier(result[0])
            logger.info(f"Using token ID: {token_id}")
            result, error = safe_api_call(client.token.get, token_id, account_id)
            print_result(f"Get Token (ID: {token_id})", result, error)
    except Exception as e:
        logger.error(f"Error in token tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_harness_apikey_endpoints(client, account_id):
    """Test Harness API key-related endpoints."""
    print_separator("TESTING HARNESS API KEY ENDPOINTS")
    logger.info("Starting Harness API key endpoint tests")
    
    try:
        # List API keys
        result, error = safe_api_call(client.harness_apikey.list, None, account_id)
        success = print_result("List Harness API Keys", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific API key
            apikey_id = get_resource_identifier(result[0])
            logger.info(f"Using API key ID: {apikey_id}")
            result, error = safe_api_call(client.harness_apikey.get, apikey_id, None, account_id)
            print_result(f"Get Harness API Key (ID: {apikey_id})", result, error)
    except Exception as e:
        logger.error(f"Error in Harness API key tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_service_account_endpoints(client, account_id):
    """Test service account-related endpoints."""
    print_separator("TESTING SERVICE ACCOUNT ENDPOINTS")
    logger.info("Starting service account endpoint tests")
    
    try:
        # List service accounts
        result, error = safe_api_call(client.service_account.list, account_id)
        success = print_result("List Service Accounts", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific service account
            service_account_id = get_resource_identifier(result[0])
            logger.info(f"Using service account ID: {service_account_id}")
            result, error = safe_api_call(client.service_account.get, service_account_id, account_id)
            print_result(f"Get Service Account (ID: {service_account_id})", result, error)
    except Exception as e:
        logger.error(f"Error in service account tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_harness_user_endpoints(client, account_id):
    """Test Harness user-related endpoints."""
    print_separator("TESTING HARNESS USER ENDPOINTS")
    logger.info("Starting Harness user endpoint tests")
    
    try:
        # List users
        result, error = safe_api_call(client.harness_user.list, account_id)
        success = print_result("List Harness Users", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific user
            user_id = get_resource_identifier(result[0])
            logger.info(f"Using user ID: {user_id}")
            result, error = safe_api_call(client.harness_user.get, user_id, account_id)
            print_result(f"Get Harness User (ID: {user_id})", result, error)
    except Exception as e:
        logger.error(f"Error in Harness user tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_harness_group_endpoints(client, account_id):
    """Test Harness group-related endpoints."""
    print_separator("TESTING HARNESS GROUP ENDPOINTS")
    logger.info("Starting Harness group endpoint tests")
    
    try:
        # List groups
        result, error = safe_api_call(client.harness_group.list, account_id)
        success = print_result("List Harness Groups", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific group
            group_id = get_resource_identifier(result[0])
            logger.info(f"Using group ID: {group_id}")
            result, error = safe_api_call(client.harness_group.get, group_id, account_id)
            print_result(f"Get Harness Group (ID: {group_id})", result, error)
    except Exception as e:
        logger.error(f"Error in Harness group tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_role_endpoints(client, account_id):
    """Test role-related endpoints."""
    print_separator("TESTING ROLE ENDPOINTS")
    logger.info("Starting role endpoint tests")
    
    try:
        # List roles
        result, error = safe_api_call(client.role.list, account_id)
        success = print_result("List Roles", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific role
            role_id = get_resource_identifier(result[0])
            logger.info(f"Using role ID: {role_id}")
            result, error = safe_api_call(client.role.get, role_id, account_id)
            print_result(f"Get Role (ID: {role_id})", result, error)
    except Exception as e:
        logger.error(f"Error in role tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_resource_group_endpoints(client, account_id):
    """Test resource group-related endpoints."""
    print_separator("TESTING RESOURCE GROUP ENDPOINTS")
    logger.info("Starting resource group endpoint tests")
    
    try:
        # List resource groups
        result, error = safe_api_call(client.resource_group.list, account_id)
        success = print_result("List Resource Groups", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific resource group
            resource_group_id = get_resource_identifier(result[0])
            logger.info(f"Using resource group ID: {resource_group_id}")
            result, error = safe_api_call(client.resource_group.get, resource_group_id, account_id)
            print_result(f"Get Resource Group (ID: {resource_group_id})", result, error)
    except Exception as e:
        logger.error(f"Error in resource group tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_role_assignment_endpoints(client, account_id):
    """Test role assignment-related endpoints."""
    print_separator("TESTING ROLE ASSIGNMENT ENDPOINTS")
    logger.info("Starting role assignment endpoint tests")
    
    try:
        # List role assignments
        result, error = safe_api_call(client.role_assignment.list, account_id)
        success = print_result("List Role Assignments", result, error)
        
        if success and result and len(result) > 0:
            # Get a specific role assignment
            role_assignment_id = get_resource_identifier(result[0])
            logger.info(f"Using role assignment ID: {role_assignment_id}")
            result, error = safe_api_call(client.role_assignment.get, role_assignment_id, account_id)
            print_result(f"Get Role Assignment (ID: {role_assignment_id})", result, error)
    except Exception as e:
        logger.error(f"Error in role assignment tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def test_harness_project_endpoints(client, account_id):
    """Test Harness project-related endpoints."""
    print_separator("TESTING HARNESS PROJECT ENDPOINTS")
    logger.info("Starting Harness project endpoint tests")
    
    try:
        # Set a timeout for the list operation
        logger.info("Attempting to list projects with a 10-second timeout")
        
        # Define a timeout handler
        def timeout_handler(signum, frame):
            logger.warning("Project list operation timed out after 10 seconds")
            raise TimeoutError("Project list operation timed out")
        
        # Set the timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        try:
            # List projects - now with error handling and timeout
            result, error = safe_api_call(client.harness_project.list, account_identifier=account_id)
            # Cancel the timeout if we get here
            signal.alarm(0)
            success = print_result("List Harness Projects", result, error)
            
            if success and result and len(result) > 0:
                # Get a specific project
                project_id = get_resource_identifier(result[0])
                logger.info(f"Using project ID: {project_id}")
                result, error = safe_api_call(client.harness_project.get, project_id, account_identifier=account_id)
                print_result(f"Get Harness Project (ID: {project_id})", result, error)
            else:
                # If listing fails, try to get a specific project if you know the ID
                project_id = input("Enter a known project ID to test (or press Enter to skip): ").strip()
                if project_id:
                    result, error = safe_api_call(client.harness_project.get, project_id, account_identifier=account_id)
                    print_result(f"Get Harness Project (ID: {project_id})", result, error)
        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            print(f"ERROR: {str(e)}")
            # Cancel the alarm
            signal.alarm(0)
            # If listing times out, try to get a specific project if you know the ID
            project_id = input("Enter a known project ID to test (or press Enter to skip): ").strip()
            if project_id:
                result, error = safe_api_call(client.harness_project.get, project_id, account_identifier=account_id)
                print_result(f"Get Harness Project (ID: {project_id})", result, error)
    except Exception as e:
        logger.error(f"Error in Harness project tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        # Make sure to cancel any pending alarms
        signal.alarm(0)

def test_split_endpoints(client):
    """Test regular Split endpoints."""
    print_separator("TESTING SPLIT ENDPOINTS")
    logger.info("Starting Split endpoint tests")
    
    try:
        # List workspaces
        result, error = safe_api_call(client.workspaces.list)
        success = print_result("List Workspaces", result, error)
        
        if not success:
            print("Unable to list workspaces. Skipping dependent tests.")
            logger.warning("Unable to list workspaces. Skipping dependent tests.")
            return
        
        if result and len(result) > 0:
            # Test across all workspaces (limited to 3 for brevity)
            for workspace_index, workspace in enumerate(result[:3]):
                # Get workspace ID
                workspace_id = get_resource_identifier(workspace)
                workspace_name = workspace.name if hasattr(workspace, 'name') else f"Workspace {workspace_index}"
                logger.info(f"Testing workspace: {workspace_name} (ID: {workspace_id})")
                
                # List environments in a workspace
                environments, error = safe_api_call(client.environments.list, workspace_id)
                env_success = print_result(f"List Environments (Workspace: {workspace_name})", environments, error)
                
                if not env_success or not environments:
                    logger.warning(f"No environments found for workspace {workspace_name}. Skipping.")
                    continue
                
                # Test across all environments (limited to 2 for brevity)
                for env_index, environment in enumerate(environments[:2]):
                    # Get environment ID
                    environment_id = get_resource_identifier(environment)
                    environment_name = environment.name if hasattr(environment, 'name') else f"Environment {env_index}"
                    logger.info(f"Testing environment: {environment_name} (ID: {environment_id})")
                    
                    # List split definitions in this environment
                    try:
                        split_defs, error = safe_api_call(client.split_definitions.list, 
                                                         environment_id, workspace_id)
                        
                        if split_defs and len(split_defs) > 0:
                            # Only show one split definition per environment
                            title = f"Split Definition (Workspace: {workspace_name}, Environment: {environment_name})"
                            print_separator(title)
                            try:
                                if hasattr(split_defs[0], '__dict__'):
                                    pprint(vars(split_defs[0]))
                                else:
                                    pprint(split_defs[0])
                                logger.info(f"Successfully displayed split definition from {environment_name}")
                            except (IndexError, TypeError):
                                print("Could not display split definition")
                                logger.error("Could not display split definition")
                        else:
                            logger.info(f"No split definitions found in environment {environment_name}")
                            print(f"No split definitions found in environment {environment_name}")
                    except Exception as e:
                        logger.error(f"Error listing split definitions: {str(e)}")
                        print(f"ERROR listing split definitions: {str(e)}")
            
            # Now get one list of splits from the first workspace
            workspace_id = get_resource_identifier(result[0])
            workspace_name = result[0].name if hasattr(result[0], 'name') else "First Workspace"
            
            # List segments in a workspace
            result, error = safe_api_call(client.segments.list, workspace_id)
            print_result(f"List Segments (Workspace ID: {workspace_id})", result, error)
                
            # List traffic types - needs workspace_id
            try:
                result, error = safe_api_call(client.traffic_types.list, workspace_id)
                print_result(f"List Traffic Types (Workspace ID: {workspace_id})", result, error)
            except Exception as e:
                logger.error(f"Error listing traffic types: {str(e)}")
                print(f"ERROR listing traffic types: {str(e)}")
            
            # Check if apikeys client has the right methods
            try:
                if hasattr(client.apikeys, 'list'):
                    result, error = safe_api_call(client.apikeys.list)
                    print_result("List API Keys", result, error)
                elif hasattr(client.apikeys, 'get_all'):
                    result, error = safe_api_call(client.apikeys.get_all)
                    print_result("List API Keys (using get_all)", result, error)
                else:
                    logger.warning("APIKeyMicroClient does not have list or get_all methods")
                    print("WARNING: APIKeyMicroClient does not have list or get_all methods")
            except Exception as e:
                logger.error(f"Error listing API keys: {str(e)}")
                print(f"ERROR listing API keys: {str(e)}")
            
            # List flag sets
            try:
                result, error = safe_api_call(client.flag_sets.list, workspace_id)
                print_result(f"List Flag Sets (Workspace ID: {workspace_id})", result, error)
            except Exception as e:
                logger.error(f"Error listing flag sets: {str(e)}")
                print(f"ERROR listing flag sets: {str(e)}")
    except Exception as e:
        logger.error(f"Error in Split endpoint tests: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

def run_harness_mode_tests(harness_client, account_id):
    """Run all Harness mode tests."""
    print_separator("RUNNING HARNESS MODE TESTS")
    logger.info("Starting Harness mode tests")
    
    # Test all Harness-specific endpoints
    test_token_endpoints(harness_client, account_id)
    test_harness_apikey_endpoints(harness_client, account_id)
    test_service_account_endpoints(harness_client, account_id)
    test_harness_user_endpoints(harness_client, account_id)
    test_harness_group_endpoints(harness_client, account_id)
    test_role_endpoints(harness_client, account_id)
    test_resource_group_endpoints(harness_client, account_id)
    test_role_assignment_endpoints(harness_client, account_id)
    test_harness_project_endpoints(harness_client, account_id)
    
    # Test regular Split endpoints in Harness mode
    test_split_endpoints(harness_client)

def run_standard_mode_tests(split_client):
    """Run standard Split mode tests."""
    print_separator("RUNNING STANDARD SPLIT MODE TESTS")
    logger.info("Starting standard Split mode tests")
    
    # Test regular Split endpoints
    test_split_endpoints(split_client)

def main():
    """Main function to run the script."""
    print("API Endpoint Tester for Split API Client")
    print("========================================")
    print("This script tests the Split API client in both standard and Harness modes.")
    print("You'll need valid API keys and account identifiers to run the tests.")
    print("\nNOTE: This script only performs read operations (GET requests) to avoid modifying any data.")
    logger.info("Script started")
    
    # Get user input for testing mode
    print("\nSelect testing mode:")
    print("1. Harness mode only")
    print("2. Split mode only")
    print("3. Both Harness and Split modes")
    print("4. Harness mode with both Harness token and Split API key")
    
    while True:
        mode = input("Enter your choice (1-4): ").strip()
        if mode in ['1', '2', '3', '4']:
            break
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    logger.info(f"Selected mode: {mode}")
    
    # Initialize variables
    account_id = None
    harness_api_key = None
    split_api_key = None
    harness_base_url = None
    split_base_url = None
    
    # Get required inputs based on selected mode
    if mode in ['1', '3', '4']:
        print("\n--- Harness Mode Configuration ---")
        print("For Harness mode, you need your account identifier and a valid Harness API key.")
        print("The account identifier is typically found in your Harness URL or account settings.")
        print("The API key should have sufficient permissions to access the resources.")
        
        account_id = input("Enter your Harness account identifier: ").strip()
        harness_api_key = input("Enter your Harness API key: ").strip()
        logger.info(f"Harness account identifier provided: {account_id}")
        logger.info("Harness API key provided (not logging the actual key)")
        
        # Ask for custom Harness base URL (optional)
        print("\nThe default Harness base URL is 'https://app.harness.io/'")
        print("This URL is only used for Harness-specific endpoints.")
        custom_harness_url = input("Enter a custom Harness base URL (or press Enter to use default): ").strip()
        if custom_harness_url:
            harness_base_url = custom_harness_url
            logger.info(f"Custom Harness base URL provided: {harness_base_url}")
        
        if not account_id or not harness_api_key:
            logger.error("Account identifier and Harness API key are required for Harness mode")
            print("Error: Account identifier and Harness API key are required for Harness mode.")
            sys.exit(1)
    
    if mode in ['2', '3', '4']:
        # For both modes, we might need to set the Split base URL
        print("\n--- Split API Configuration ---")
        print("The default Split base URLs are:")
        print("- 'https://api.split.io/internal/api/v2' (for v2 endpoints)")
        print("- 'https://api.split.io/api/v3' (for v3 endpoints)")
        print("- 'https://api.split.io/internal/api/v1' (for v1 endpoints)")
        custom_split_url = input("Enter a custom Split base URL (or press Enter to use default): ").strip()
        if custom_split_url:
            split_base_url = custom_split_url
            logger.info(f"Custom Split base URL provided: {split_base_url}")
    
    if mode in ['2', '3', '4']:
        print("\n--- Split API Key Configuration ---")
        print("For Split mode, you need a valid Split API key with sufficient permissions.")
        print("You can find your API keys in the Split dashboard under 'API Keys' section.")
        print("If you don't provide a Split API key and are also testing Harness mode,")
        print("the Harness API token will be used for Split endpoints.")
        
        split_api_key = input("Enter your Split API key (or press Enter to use Harness token if available): ").strip()
        if split_api_key:
            logger.info("Split API key provided (not logging the actual key)")
        elif mode == '3' and harness_api_key:
            logger.info("No Split API key provided, will use Harness token for Split endpoints")
        else:
            logger.error("Split API key is required for Split mode when not testing Harness mode")
            print("Error: Split API key is required for Split mode when not testing Harness mode.")
            sys.exit(1)
    
    # Select which endpoints to test
    print("\n--- Select Endpoints to Test ---")
    print("You can choose to test specific endpoints or all endpoints.")
    print("Available endpoint groups:")
    
    harness_endpoints = {
        '1': ('token', test_token_endpoints),
        '2': ('harness_apikey', test_harness_apikey_endpoints),
        '3': ('service_account', test_service_account_endpoints),
        '4': ('harness_user', test_harness_user_endpoints),
        '5': ('harness_group', test_harness_group_endpoints),
        '6': ('role', test_role_endpoints),
        '7': ('resource_group', test_resource_group_endpoints),
        '8': ('role_assignment', test_role_assignment_endpoints),
        '9': ('harness_project', test_harness_project_endpoints)
    }
    
    split_endpoints = {
        '10': ('split', test_split_endpoints)
    }
    
    # Display available endpoints based on selected mode
    available_endpoints = {}
    
    if mode in ['1', '3', '4']:
        print("\nHarness Endpoints:")
        for key, (name, _) in harness_endpoints.items():
            print(f"{key}. {name}")
            available_endpoints[key] = harness_endpoints[key]
        
        # Also include Split endpoints when in Harness mode
        print("\nSplit Endpoints (accessible in Harness mode):")
        for key, (name, _) in split_endpoints.items():
            print(f"{key}. {name}")
            available_endpoints[key] = split_endpoints[key]
    
    if mode in ['2']:
        print("\nSplit Endpoints:")
        for key, (name, _) in split_endpoints.items():
            print(f"{key}. {name}")
            available_endpoints[key] = split_endpoints[key]
    
    print("\n0. All available endpoints")
    
    # Get user selection
    endpoint_selection = input("\nEnter the numbers of the endpoints to test (comma-separated, or 0 for all): ").strip()
    selected_endpoints = []
    
    if endpoint_selection == '0':
        # Select all available endpoints
        selected_endpoints = list(available_endpoints.values())
    else:
        # Parse the comma-separated list
        try:
            endpoint_numbers = [num.strip() for num in endpoint_selection.split(',')]
            for num in endpoint_numbers:
                if num in available_endpoints:
                    selected_endpoints.append(available_endpoints[num])
                else:
                    print(f"Warning: Invalid endpoint number '{num}'. Skipping.")
        except Exception as e:
            logger.error(f"Error parsing endpoint selection: {str(e)}")
            print(f"Error parsing endpoint selection: {str(e)}")
            print("Testing all available endpoints instead.")
            selected_endpoints = list(available_endpoints.values())
    
    # Run tests based on selected mode
    if mode in ['1', '3', '4']:
        print("\nInitializing Split API client in Harness mode...")
        
        try:
            # Initialize the client in Harness mode
            config = {
                'harness_mode': True,
                'harness_token': harness_api_key,
                'account_identifier': account_id
            }
            
            # Add Split API key for mode 4
            if mode == '4' and split_api_key:
                config['apikey'] = split_api_key
                logger.info("Using both Harness token and Split API key")
            
            # Add custom Harness base URL if provided
            if harness_base_url:
                config['harness_base_url'] = harness_base_url
                
            # Add custom Split base URL if provided
            if split_base_url:
                config['base_url'] = split_base_url
            
            logger.info(f"Initializing Harness mode client with config keys: {list(config.keys())}")
            harness_client = get_client(config)
            
            print("Harness mode client initialized successfully.")
            logger.info("Harness mode client initialized successfully")
            
            # Run selected Harness endpoints
            print_separator("RUNNING HARNESS MODE TESTS")
            logger.info("Starting Harness mode tests")
            
            for name, test_func in selected_endpoints:
                if test_func in [func for _, func in harness_endpoints.values()]:
                    test_func(harness_client, account_id)
                elif test_func in [func for _, func in split_endpoints.values()]:
                    test_func(harness_client)
        except Exception as e:
            logger.error(f"Error initializing Harness mode client: {str(e)}", exc_info=True)
            print(f"Error initializing Harness mode client: {str(e)}")
            print("Please check your account identifier and API key and try again.")
    
    if mode in ['2']:
        print("\nInitializing Split API client in standard mode...")
        
        try:
            # Initialize the client in standard mode
            config = {
                'apikey': split_api_key
            }
            
            # Add custom Split base URL if provided
            if split_base_url:
                config['base_url'] = split_base_url
            
            logger.info(f"Initializing standard mode client with config keys: {list(config.keys())}")
            split_client = get_client(config)
            
            print("Standard mode client initialized successfully.")
            logger.info("Standard mode client initialized successfully")
            
            # Run selected Split endpoints
            print_separator("RUNNING STANDARD SPLIT MODE TESTS")
            logger.info("Starting standard Split mode tests")
            
            for name, test_func in selected_endpoints:
                if test_func in [func for _, func in split_endpoints.values()]:
                    test_func(split_client)
        except Exception as e:
            logger.error(f"Error initializing standard mode client: {str(e)}", exc_info=True)
            print(f"Error initializing standard mode client: {str(e)}")
            print("Please check your API key and try again.")
    
    print_separator("TESTING COMPLETE")
    print("All tests have been completed. Review the output above for results.")
    print("\nIf you encountered authentication errors, please verify your credentials and try again.")
    print("For Harness mode, ensure your account identifier is correct and your API key has the necessary permissions.")
    print("For Split mode, ensure your API key is valid and has the required permissions.")
    
    # Print information about the API architecture
    print("\nAPI Architecture Information:")
    print("1. Split endpoints:")
    print("   - Always use the Split base URLs (e.g., https://api.split.io/internal/api/v2)")
    print("   - In standard mode: authenticated with Split API key")
    print("   - In Harness mode: authenticated with Split API key or Harness token")
    print("   - If Split API key is not provided in combined mode, Harness token will be used")
    
    if mode in ['1', '3', '4']:
        print("\n2. Harness-specific endpoints:")
        print("   - Use the Harness base URL (default: https://app.harness.io/)")
        print("   - Authenticated with 'x-api-key' header instead of standard Split authentication")
        print("   - If harness_token is not provided, apikey will be used for all operations")
    
    logger.info("Script completed")

if __name__ == "__main__":
    main()
