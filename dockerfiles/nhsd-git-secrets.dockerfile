# This dockerfile allows you to run the NHS flavour of secret-scanning on the mounted directory.
# It assumes nothing about the local filesystem, so can be built remotely by using 
#    docker build -t git-secrets -f https://raw.githubusercontent.com/NHSDigital/eps-common-workflows/refs/tags/<VERSION>/dockerfiles/nhsd-git-secrets.dockerfile .
# When run:
#    docker run -v /path/to/code:/src git-secrets [ARGS]
# It will default to scanning the local directory (note that it must be a git repository) as it currently is (no history scan).
# However, script arguments (https://github.com/NHSDigital/software-engineering-quality-framework/blob/main/tools/nhsd-git-secrets/git-secrets)
# can also be supplied. Remember to provide the trailing `.`, or the script would assume 
# you want to scan STDIN.
# The default arguments are `--scan -r .

FROM ubuntu:latest

RUN echo "Installing required modules"
RUN apt-get update
RUN apt-get -y install curl git build-essential

WORKDIR /secrets-scanner

RUN echo "Downloading secrets scanner"
RUN curl https://codeload.github.com/awslabs/git-secrets/tar.gz/master | tar -xz --strip=1 git-secrets-master

RUN echo "Installing secrets scanner"
RUN make install

RUN echo "Downloading regex files from engineering-framework"
RUN curl https://codeload.github.com/NHSDigital/software-engineering-quality-framework/tar.gz/main | tar -xz --strip=3 software-engineering-quality-framework-main/tools/nhsd-git-secrets/nhsd-rules-deny.txt

RUN echo '#!/usr/bin/env bash\n\
\n\
git config --global --add safe.directory /src\n\
# Register additional providers: adds AWS by default \n\
echo "Configuring secrets scanner" \n\
/secrets-scanner/git-secrets --register-aws \n\
/secrets-scanner/git-secrets --add-provider -- cat /secrets-scanner/nhsd-rules-deny.txt \n\
\n\
/secrets-scanner/git-secrets $@ \n ' >> /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /src
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "--scan", "-r", "." ]
