# cd /home/ususariobase
CROSSTOOLS_HOME=/opt/crosstool/gcc-2.95.3-glibc-2.1.3
ARCH=i386

PREFIX=${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu
PATH=${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu/bin:${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu/${ARCH}-unknown-linux-gnu/bin:$PATH
LIBRARY_PATH=${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu/${ARCH}-unknown-linux-gnu/usr:${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu/${ARCH}-unknown-linux-gnu/usr/X11R6/lib
alias ld="${CROSSTOOLS_HOME}/${ARCH}-unknown-linux-gnu/bin/${ARCH}-unknown-linux-gnu-ld"

export TARGET PREFIX TARGET_PREFIX PATH LIBRARY_PATH
