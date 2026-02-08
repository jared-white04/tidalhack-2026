import boto3
import json
import os
import pandas as pd
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Extract AWS Credentials
aws_access  = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret  = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session = os.getenv("AWS_SESSION_TOKEN")  # Mandatory for Assumed Roles
aws_region  = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

# 3. Initialize Bedrock Runtime Client
# We use the full "Triple" of credentials to ensure the signature is valid.
try:
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=aws_region,
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret,
        aws_session_token=aws_session
    )
except Exception as e:
    print(f"❌ Failed to initialize Bedrock client: {e}")

def get_column_mapping_bedrock(file_path, targets):
    """
    Reads CSV headers and uses Claude 3 to map them to target data needs.
    """
    # Load headers with latin1 encoding to handle special characters like °
    try:
        df = pd.read_csv(file_path, nrows=0, encoding='latin1')
        actual_headers = list(df.columns)
    except Exception as e:
        print(f"❌ Error reading file headers: {e}")
        return None

    # Define the mapping prompt
    prompt = f"""You are a pipeline integrity data expert. 
    Map these ILI spreadsheet headers: {actual_headers} 
    to these target categories: {targets}.
    
    Rules:
    1. Return ONLY a valid JSON object.
    2. Key = Target Name, Value = Integer Index (starting at 0).
    3. Use null if a category is not found.
    4. Match based on common industry synonyms (e.g., 'Orientation' -> 'clock_position')."""

    # Claude 3 Sonnet Payload
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    try:
        # Invoke the Model
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # Parse Response
        response_body = json.loads(response.get("body").read())
        raw_text = response_body['content'][0]['text']
        
        # Strip potential markdown code blocks
        clean_json = raw_text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)

    except Exception as e:
        print(f"❌ Bedrock Invocation Error: {e}")
        return None

# --- EXECUTION ---
if __name__ == "__main__":
    target_needs = [
        'feature_id',
        'distance',
        'odometer',
        'joint_number',
        'relative_position',
        'angle',
        'feature_type',
        'depth_percent',
        'length',
        'width',
        'wall_thickness',
        'weld_type',
        'elevation'
    ]
    csv_file = "test.csv" # Replace with your actual filename

    mapping = get_column_mapping_bedrock(csv_file, target_needs)

    if mapping:
        print("\n✅ Successfully mapped headers:")
        print(json.dumps(mapping, indent=4))
    else:
        print("\n❌ Failed to generate mapping.")