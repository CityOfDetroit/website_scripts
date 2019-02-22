#!/usr/bin/env bash

for lang in "ar" "bn" "es"
do

    # echo ${lang}

    for file in $( cat crio_urls.txt )
    do

        # echo ${file}

        if [ ! -e translated_content/${lang}/${file} ]
        then

            echo "file translated_content/${lang}/${file} not found"
            exit 1

        else

            ./load_translation.py ${lang} translated_content/${lang}/${file}

        fi

        sleep 1

    done

done

exit 0
