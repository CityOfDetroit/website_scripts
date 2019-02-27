#!/usr/bin/env bash

for dir in translated_content/*
do

    for filename in ${dir}/*.txt
    do

        ./has_bad_content.py ${filename}
        if [ $? -eq 1 ]
        then

            echo ${filename}

        fi

    done

done
