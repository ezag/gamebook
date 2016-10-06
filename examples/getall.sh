DESTDIR=`date '+%Y%m%d%H%M%S'`
mkdir $DESTDIR
while read url; do
    GAMEKEY=`basename \`dirname $url\``
    cmd="gb-url-to-db $url $GAMEKEY postgres://zag@localhost/gamebook"
    echo $cmd
    $cmd 2>$DESTDIR/$GAMEKEY.log
done < gamebooks.txt
