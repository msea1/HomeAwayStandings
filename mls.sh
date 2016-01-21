#!/bin/bash
cd ~/cron/mls_table
source bin/activate

python mls.py

cp mls_table.cache ~/statcorner.com/cache/mls_table.cache
