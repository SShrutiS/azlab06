from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *
from datetime import datetime, timedelta
import time

def print_item(group):
    """Print an Azure object instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    if hasattr(group, 'location'):
        print("\tLocation: {}".format(group.location))
    if hasattr(group, 'tags'):
        print("\tTags: {}".format(group.tags))
    if hasattr(group, 'properties'):
        print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and hasattr(props, 'provisioning_state') and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")

def print_activity_run_details(activity_run):
    """Print activity run details."""
    print("\n\tActivity run details\n")
    print("\tActivity run status: {}".format(activity_run.status))    
    if activity_run.status == 'Succeeded':
        print("\tNumber of bytes read: {}".format(activity_run.output['dataRead']))       
        print("\tNumber of bytes written: {}".format(activity_run.output['dataWritten']))           
        print("\tCopy duration: {}".format(activity_run.output['copyDuration']))           
    else:
        print("\tErrors: {}".format(activity_run.error['message']))
        
def print_item(group):
    """Print an Azure object instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    if hasattr(group, 'location'):
        print("\tLocation: {}".format(group.location))
    if hasattr(group, 'tags'):
        print("\tTags: {}".format(group.tags))
    if hasattr(group, 'properties'):
        print_properties(group.properties)

def main():

# Azure subscription ID
    subscription_id = '86d62b86-1ed2-45c1-8f6c-164c9b3db93a'

# This program creates this resource group. If it's an existing resource group, comment out the code that creates the resource group
    rg_name = 'sshResourceGroup'

# The data factory name. It must be globally unique.
    df_name = 'sshDF'

# Specify your Active Directory client ID, client secret, and tenant ID
    credentials = ServicePrincipalCredentials(client_id='276d4d10-d006-48e0-a360-572267e5d400', secret='aphJTM107vbXsrJLC9Ehsk9S2pLxysvGycWnxVE4pjc=', tenant='da67ef1b-ca59-4db2-9a8c-aa8d94617a16')
    resource_client = ResourceManagementClient(credentials, subscription_id)
    adf_client = DataFactoryManagementClient(credentials, subscription_id)

    rg_params = {'location':'westus'}
    df_params = {'location':'westus'}
    
# Create the resource group
# Comment out if the resource group already exits
    resource_client.resource_groups.create_or_update(rg_name, rg_params)
    
# Create the resource group
# Comment out if the resource group already exits
    resource_client.resource_groups.create_or_update(rg_name, rg_params)

# Create a data factory
    df_resource = Factory(location='westus')
    df = adf_client.factories.create_or_update(rg_name, df_name, df_resource)
    print_item(df)
    while df.provisioning_state != 'Succeeded':
        df = adf_client.factories.get(rg_name, df_name)
        time.sleep(1)
        
# Create an Azure Storage linked service
    ls_name = 'storageLinkedService'

# IMPORTANT: specify the name and key of your Azure Storage account
    storage_string = SecureString('DefaultEndpointsProtocol=https;AccountName=sshstorageaccount03;AccountKey=et+CstqRneJos+tjRAZcjubCdc2kdpBhISErdyIG/t94iLcrYAKSdD0txJjvR3C7wCrSz+9mcdjJAl05jGlChw==')

    ls_azure_storage = AzureStorageLinkedService(connection_string=storage_string)
    ls = adf_client.linked_services.create_or_update(rg_name, df_name, ls_name, ls_azure_storage)
    print_item(ls) 
    
# Create an Azure blob dataset (input)
    ds_name = 'dset_in'
    ds_ls = LinkedServiceReference(ls_name)
    blob_path= 'playerscontainer/myteam'
    blob_filename = 'astroplayers.txt'
    ds_azure_blob= AzureBlobDataset(ds_ls, folder_path=blob_path, file_name = blob_filename)
    ds = adf_client.datasets.create_or_update(rg_name, df_name, ds_name, ds_azure_blob)
    print_item(ds)
    
# Create an Azure blob dataset (output)
    dsOut_name = 'dset_out'
    output_blobpath = 'playerscontainer/output'
    dsOut_azure_blob = AzureBlobDataset(ds_ls, folder_path=output_blobpath)
    dsOut = adf_client.datasets.create_or_update(rg_name, df_name, dsOut_name, dsOut_azure_blob)
    print_item(dsOut)
    
# Create a copy activity
    act_name =  'copyBlobPleayerstoBlob'
    blob_source = BlobSource()
    blob_sink = BlobSink()
    dsin_ref = DatasetReference(ds_name)
    dsOut_ref = DatasetReference(dsOut_name)
    copy_activity = CopyActivity(act_name,inputs=[dsin_ref], outputs=[dsOut_ref], source=blob_source, sink=blob_sink)

# Create a pipeline with the copy activity
    p_name =  'copyPipeliness'
    params_for_pipeline = {}
    p_obj = PipelineResource(activities=[copy_activity], parameters=params_for_pipeline)
    p = adf_client.pipelines.create_or_update(rg_name, df_name, p_name, p_obj)
    print_item(p)
    
# Create a pipeline run.
    run_response = adf_client.pipelines.create_run(rg_name, df_name, p_name,
        {
        }
    )
    
# Monitor the pipeline run
    time.sleep(30)
    pipeline_run = adf_client.pipeline_runs.get(rg_name, df_name, run_response.run_id)
    print("\n\tPipeline run status: {}".format(pipeline_run.status))
    activity_runs_paged = list(adf_client.activity_runs.list_by_pipeline_run(rg_name, df_name, pipeline_run.run_id, datetime.now() - timedelta(1),  datetime.now() + timedelta(1)))
    print_activity_run_details(activity_runs_paged[0])

# Start the main method
main()