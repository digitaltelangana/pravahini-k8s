gen_pw() {
  head -c 24 /dev/urandom | base64 | tr "/+" "_-"
}

rm -f grpc-internal-keystore.p12

# generate EC keypair and self-signed certificate for internal transport
gen_grpc_internal_keypair() {
    local keystore_pw="xroad123"   #"$(gen_pw)"
    echo "Keystore password: $keystore_pw"
    local keystore="./grpc-internal-keystore.p12"

    PW="$keystore_pw" \
    keytool -genkeypair -alias grpc-internal \
    -storetype PKCS12 \
    -keyalg EC -groupname secp256r1 \
    -sigalg SHA256withECDSA \
    -keystore "$keystore" \
    -dname "CN=127.0.0.1" \
    -ext "SAN:c=DNS:localhost,IP:127.0.0.1" \
    -validity 3650 \
    -storepass:env PW \
    -keypass:env PW
    # echo base64 encoded keystore
    base64 -i "$keystore"
}

echo "Generating gRPC internal keypair..."
gen_grpc_internal_keypair
echo "Done."