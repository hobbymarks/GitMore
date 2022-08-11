#!/usr/bin/env bash

##get package name to build
package=$1

if [[ -z "$package" ]]; then
    echo "Usage: $0 <package-name>"
    exit 1
fi

##set output app name
app="giat"

##get version
# ver=$(git tag -l --sort=-creatordate | head -n 1)
ver="0.0.3"
##get commit index
# cidx=$(git rev-parse HEAD | cut -c1-7)
##get build date
# bldate=$(date '+%Y%m%d.%H%M%S')

###############################################################################
echo ""
echo "==>go build ..."
echo ""

##loop platform to build
platforms=("windows/amd64" "windows/386" "darwin/amd64" "linux/amd64" "linux/386")
for platform in "${platforms[@]}"; do
    platform_split=(${platform//\// })
    GOOS=${platform_split[0]}
    GOARCH=${platform_split[1]}

    output_name=$app'-'$GOOS'-'$GOARCH'-'$ver

    if [ $GOOS = "windows" ]; then
        output_name+='.exe'
    fi

    env GOOS=$GOOS GOARCH=$GOARCH go build -ldflags "-X 'github.com/hobbymarks/giat/cmd.version=$ver' -s -w" -o dist/$output_name $package
    if [ $? -ne 0 ]; then
        echo 'An error has occured! Aborting the script execution...'
        exit 1
    else
        echo "$output_name"
    fi
done

##zip all platforms app together
###############################################################################
if command -v zip &>/dev/null; then
    echo ""
    echo "==>zip together ..."
    echo ""

    cd dist
    find $app*$ver* -type f | xargs zip $app-$ver.zip
    cd ..
fi

##reduce app size by upx (https://upx.github.io/)
###############################################################################
# if command -v upx &>/dev/null; then
#     cd dist

#     echo ""
#     echo "==>upx compressing ..."
#     echo ""

#     find $app*$ver* -executable -type f | xargs upx --brute

#     # printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -

#     echo ""
#     echo "==>zip upx together ..."
#     echo ""

#     find $app*$ver* -type f | xargs zip $app-$ver.upx.zip

#     cd ..
#     # printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
# fi
