import os, json, time, secrets, string
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "tinyqr_links")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

ALPHABET = string.ascii_letters + string.digits

# 추가: API 응답 헤더(나중에 브라우저/프론트 연동할 때 필요)
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def gen_code(length=6):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def lambda_handler(event, context):
    try:
        body = event.get("body")
        if isinstance(body, str) and body:
            data = json.loads(body)
        elif isinstance(body, dict):
            data = body
        else:
            data = event or {}

        url = data.get("url") or data.get("longUrl")
        if not url or not isinstance(url, str):
            return {
                "statusCode": 400,
                "headers": DEFAULT_HEADERS,
                "body": json.dumps({"error": "url is required"})
            }

        if not (url.startswith("http://") or url.startswith("https://")):
            return {
                "statusCode": 400,
                "headers": DEFAULT_HEADERS,
                "body": json.dumps({"error": "url must start with http:// or https://"})
            }

        ttl_days = int(data.get("ttlDays", 30))
        ttl_days = max(1, min(ttl_days, 365))

        now = int(time.time())
        expires_at = now + ttl_days * 86400

        code = None
        for _ in range(8):
            candidate = gen_code(6)
            try:
                table.put_item(
                    Item={
                        "code": candidate,
                        "url": url,
                        "createdAt": now,
                        "expiresAt": expires_at,
                        "clicks": 0
                    },
                    ConditionExpression="attribute_not_exists(code)"
                )
                code = candidate
                break
            except ClientError as e:
                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    continue
                raise

        if not code:
            return {
                "statusCode": 500,
                "headers": DEFAULT_HEADERS,
                "body": json.dumps({"error": "failed to allocate code"})
            }

        return {
            "statusCode": 200,
            "headers": DEFAULT_HEADERS,
            "body": json.dumps({"code": code, "url": url, "expiresAt": expires_at})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": DEFAULT_HEADERS,
            "body": json.dumps({"error": "internal_error", "detail": str(e)})
        }
