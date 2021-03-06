import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key



###15616515161
example_Event = {
    "UUID": "4ed4b0da-9a1e-11ec-b909-0242ac120002",
    "awsAccountID": "1561651523161",
    "awsEnvironment": "HOM", 
    "awsAccountName": "analytics-test-example",
    "idCloud": "391709f1-2fd2-4512-86e2-cb770716c7b8", 
}   


ddb_client = boto3.client('dynamodb', "us-east-1")
ddb_resource = boto3.resource("dynamodb", "us-east-1")

awsAccountID = example_Event['awsAccountID']
awsEnvironment = example_Event['awsEnvironment']
idCloud = example_Event['idCloud']


def query_ddb_asset(awsAccountID):
    ddb_table = ddb_resource.Table("control_asset")
    try:
        response = ddb_table.query(
            KeyConditionExpression=Key('awsAccountID').eq(example_Event['awsAccountID'])
        )
        responseQuery = response["Items"]
        
        responseQuery_secondary = ddb_table.query(
            IndexName='idCloud-index',
            KeyConditionExpression=Key('idCloud').eq(idCloud)
        )
        responseQuery_globalSecondaryIndex = responseQuery_secondary['Items']
        
        if not responseQuery:
            if awsEnvironment == "DEV":
                print("Não existe response da Query nesse account ID ")
                print("--------------------------------------------")
                if not responseQuery_globalSecondaryIndex:
                    print("Não existe registros desse idCloudIndex")
                    print("Posso fazer o put dos itens aqui")
                    
                else:
                    for i in range(len(responseQuery_globalSecondaryIndex)): 
                        if responseQuery_globalSecondaryIndex[i]['environment'] == "DEV":
                            print("O ambiente de DEV já foi registrado nesse SecondaryIndex")
                
            elif awsEnvironment == "HOM":
                print("Não existe response da Query nesse account ID ")
                print("--------------------------------------------")
                
                if not responseQuery_globalSecondaryIndex:
                    print("Não existe registros desse idCloudIndex")
                    
                else:
                    if len(responseQuery_globalSecondaryIndex) > 1 : 
                        exists_dev_environment = 'DEV' in responseQuery_globalSecondaryIndex[0]['environment']
                        exists_hom_environment = 'HOM' in responseQuery_globalSecondaryIndex[1]['environment']
                        print("Dev Environment exists? ", exists_dev_environment)
                        print("Hom Environment exists? ", exists_hom_environment)
                        if exists_dev_environment == True and exists_hom_environment == True:
                            print("O ambiente de DEV já foi registrado nesse SecondaryIndex")
                            print("O ambiente de HOM já foi registrado nesse SecondaryIndex")
                            print(f"Não foi possível tornar a conta {awsAccountID} uma PRODUCER em ambiente de {awsEnvironment}, pois ela ja é!")
                        elif exists_dev_environment == False and exists_hom_environment == False:   
                            print("O ambiente de DEV precisa ser registrado para fazer HOM")
                        
                    elif len(responseQuery_globalSecondaryIndex) == 1:
                        exists_dev_environment = 'DEV' in responseQuery_globalSecondaryIndex[0]['environment']
                        exists_hom_environment = False
                        print("Dev Environment exists? ", exists_dev_environment)
                        print("Hom Environment exists? ", exists_hom_environment)
                        
                        if exists_dev_environment == True and exists_hom_environment == False:   
                            print("O ambiente de DEV já foi registrado nesse SecondaryIndex")
                            print("Posso fazer o put dos itens aqui")
                        
                        elif exists_dev_environment == False and exists_hom_environment == True:
                            print("Erro de ambientes, não é possível o HOM estar registrado sem dev")
               
                
            elif awsEnvironment == "PRO":
                print("Aqui é PRO")
                
            else:
                print("O awsEnvironment no payload é inválido, favor validar se é igual (DEV, HOM ou PRO)")
                
        else:
            print("Existe response da Query nesse account ID ")
            if (responseQuery[0]['environment']) == example_Event['awsEnvironment']:
                if not responseQuery_globalSecondaryIndex:
                    print("Não posso fazer o put, pois existe response nessa AccountID")
                    
                else:
                    for i in range(len(responseQuery_globalSecondaryIndex)): 
                        if responseQuery_globalSecondaryIndex[i]['environment'] == "DEV":
                            print("O ambiente de DEV já foi registrado nesse SecondaryIndex")
                            print(f"Não foi possível tornar a conta {awsAccountID} uma PRODUCER em ambiente de {awsEnvironment}, pois ela ja é!")

                
            elif (responseQuery[0]['environment']) == "HOM":
                responseQuery_secondary = ddb_table.query(
                    IndexName='idCloud-index',
                    KeyConditionExpression=Key('idCloud').eq(idCloud)
                )
                print("Esse é o resultado do index secundário", responseQuery_secondary)
                
                
   
    except ClientError as e:
        print(f" A account ID inserida não está registrada na tabela de asset.  {e}")
        return e
        
        

def lambda_handler(event, context):
    query_ddb_asset(awsAccountID)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
