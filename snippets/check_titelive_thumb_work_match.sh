cat ~/workspace/pc/code/api/ftp_mirrors/titelive_works/livre3_11/Quotidien*.tit | cut -d\~ -f1 | sort -u > tit_eans
head tit_eans
for i in ~/workspace/pc/code/api/ftp_mirrors/titelive_works/Atoo/livres_tl*.zip; do zipinfo -1 "$i" | sed -e 's#^.*/##' -e 's/_.*$//'; done | sort -u > thumb_eans
head thumb_eans
comm -1 -2 tit_eans thumb_eans