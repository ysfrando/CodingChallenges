import boto3 
import json
from datetime import datetime


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    securityhub = boto3.client('securityhub')

    def check_bucket_security(bucket_name):
        findings = []
        
        try:
            # Check public access settings
            public_access = s3.get_public_access_block(Bucket=bucket_name)
            if not all(public_access['PublicAccessBlockConfiguraton']).values():
                findings.append({
                    'Title': 'S3 Bucket Public Access Not Fully Restricted',
                    'Description': f'Bucket {bucket_name} has some public access blocks disabled',
                    'Severity': 'HIGH'
                })
            
            # Check encryption
            encryption = s3.get_bucket_encryption(Bucket=bucket_name)
            if 'ServerSideEncryptionConfiguration' not in encryption:
                findings.append({
                    'Title': 'S3 Bucket Missing Default Encryption',
                    'Description': f'Bucket {bucket_name} does not have default encryption enabled',
                    'Severity': 'MEDIUM'
                })
          
            # Check logging
            logging = s3.get_bucket_logging(Bucket=bucket_name)
            if 'LoggingEnabled' not in logging:
                findings.append({
                    'Title': 'S3 Bucket Logging Not Enabled',
                    'Description': f'Bucket {bucket_name} does not have access logging enabled',
                    'Severity': 'LOW'
                })
            
            # Check versioning
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
            if 'Status' not in versioning or versioning['Status'] != 'Enabled':
                findings.append({
                    'Title': 'S3 Bucket Versioning Not Enabled',
                    'Description': 'Bucket {bucket_name} does not have versioning enabled',
                    'Severity': 'LOW'
                })
             
            return findings

        except Exception as e:
            print(f"Error checking bucket {bucket_name}: {str(e)}")
            return []

    buckets = s3.list_buckets()['Buckets']
    
    for bucket in buckets:
        findings = check_bucket_security(bucket['Name'])

        for finding in findings:
            securityhub.batch_import_findings(
                Findings=[
                    {
                        'SchemaVersion': '2018-10-08',
                        'Id': f"{bucket['Name']}/{finding['Title']}",
                        'ProductArn': f'arn:aws:securityhub:{context.invoked_function_arn.split(":")[3]}::product/custom-security-scanner',
                        'GeneratorId': 's3-security-scanner',
                        'AwsAccountId': context.invoked_function_arn.split(":")[4],
                        'Types': ['Software and Configuration Checks/AWS Security Best Practices'],
                        'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                        'UpdatedAt': datetime.utcnow().isoformat() + 'Z',
                        'Severity': {
                            'Label': finding['Severity']
                        },
                        'Title': finding['Title'],
                        'Description': finding['Description'],
                        'Resources': [
                            {
                                'Type': 'AwsS3Bucket',
                                'Id': f'arn:aws:s3:::{bucket["Name"]}'
                            }
                        ]
                    }
                ]
            )


    return {
        'statusCode': 200,
        'body': json.dumps('S3 security scan completed')
    } 
    
