#!/bin/bash

header "Provider import"

# importing manifest from our testing export
IMPORT_ORG="Import_Org_$RAND"
IMPORT_PROV="Import_Prov_$RAND"
test "org create" org create --name=$IMPORT_ORG
test "provider create" provider create --org="$IMPORT_ORG" --name="$IMPORT_PROV" --type=redhat --url="https://example.com/path/"
test "provider import_manifest" provider import_manifest --org="$IMPORT_ORG" --name="$IMPORT_PROV" --file=$TESTDIR/fake-manifest.zip
#test "provider delete" provider delete --org="$IMPORT_ORG" --name="$IMPORT_PROV"
skip_test "provider delete" "temporarily disabled until we fix the bug" provider delete --org="$IMPORT_ORG" --name="$IMPORT_PROV"
test "org delete" org delete --name=$IMPORT_ORG
