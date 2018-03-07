#!/bin/bash
lftp -u $TITELIVE1_FTP_LOGIN,$TITELIVE1_FTP_PASSWORD -e "mirror  --parallel=3 --verbose / /home/deploy/pass-culture-main/api/ftp_mirrors/titelive_works; quit" ftp.astitelive.com
lftp -u $TITELIVE2_FTP_LOGIN,$TITELIVE2_FTP_PASSWORD -e "mirror  --parallel=3 --verbose / /home/deploy/pass-culture-main/api/ftp_mirrors/titelive_offers; quit" ftp.astitelive.com
