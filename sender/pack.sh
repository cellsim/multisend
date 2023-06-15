#!/bin/bash

PACKAGE_NAME="cellsim"
VERSION="1.1"
BUILD_NAME=$PACKAGE_NAME"_"$VERSION

ARCH=$(dpkg --print-architecture)

if [ -d $BUILD_NAME ]; then
    rm -rf $BUILD_NAME
fi

# echo $ARCH
# exit 0

mkdir $BUILD_NAME
mkdir $BUILD_NAME/DEBIAN

cat << EOF > $BUILD_NAME/DEBIAN/control
Package: $PACKAGE_NAME
Version: $VERSION
Priority: optional
Architecture: $ARCH
Depends: ethtool
Maintainer: Jeromy Fu
Description: Cellsim
 Cellular network bandwidth simulator
EOF

cat << EOF > $BUILD_NAME/DEBIAN/postinst
#!/bin/bash
ln -sf /opt/cellsim/cellsim /sbin/cellsim
echo "Init the setup: \"/opt/cellsim/cellsim-env.sh setup [ingress] [egress]\""
echo "To run cellsim emulator:"
echo "nohup sudo cellsim [uplink_trace] [downlink_trace] [loss] [ingress] [egress] > /tmp/cellsim-stdout 2>/tmp/cellsim-stderr"
echo "Preinstalled trace files can be found at \"/opt/cellsim/traces\""
echo "To stop cellsim emulator:"
echo "killall cellsim"
echo "Teardown: \"/opt/cellsim/cellsim-env.sh teardown [ingress] [egress]\""
EOF
chmod +x $BUILD_NAME/DEBIAN/postinst

mkdir -p $BUILD_NAME/opt/cellsim
cp cellsim $BUILD_NAME/opt/cellsim/cellsim
cp cellsim-env.sh $BUILD_NAME/opt/cellsim/cellsim-env.sh
cp -R traces $BUILD_NAME/opt/cellsim/

dpkg -b $BUILD_NAME
