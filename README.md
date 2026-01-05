Smart Filtering Deployment Commands
# Run local test with the SmartFiltering agent
python3 -m my_agent.deployment.local

# Create a new deployment
python3 -m my_agent.deployment.remote --create

# List all deployments
python3 -m my_agent.deployment.remote --list

# Delete a deployment
python3 -m my_agent.deployment.remote --delete --resource_id <RESOURCE_ID>

# Create a session for a deployed agent
python3 -m my_agent.deployment.remote --create_session --resource_id <RESOURCE_ID> --user_id test_user

# List sessions for a user
python3 -m my_agent.deployment.remote --list_sessions --resource_id <RESOURCE_ID> --user_id test_user

# Get session details
python3 -m my_agent.deployment.remote --get_session --resource_id <RESOURCE_ID> --session_id <SESSION_ID>

# Send a message to deployed agent
python3 -m my_agent.deployment.remote --send --resource_id 8589425518116339712 --session_id 498696418039431168 --message "xxx"