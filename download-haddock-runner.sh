#!/bin/bash

# Download the latest release of the `haddock-runner`
export VERSION="1.7.0"
export URL=https://github.com/haddocking/haddock-runner/releases/download/v${VERSION}/haddock-runner_${VERSION}_linux_386.tar.gz

# Download and extract the binary
mkdir -p bin/
cd bin/
wget -qO- ${URL} | tar xvz
rm LICENSE README.md
chmod +x haddock-runner
cd -
mv bin/haddock-runner .
