#!/bin/bash
#
# The script finds routers with a Yggdrasil IPv6
# and mixes 30% of regular routers with them.
#
# If Yggdrasil < 25 then regular routers 25;
#
# Путь до папки netDb, которая будет скопирована
netdb=/var/lib/i2pd/netDb
# Путь до выходной папки
outdb=/srv/pyseeder/transitoutput
#
###
temp=/tmp/yggreseed
success=/tmp/yggreseed.success
padding=/tmp/yggreseed.padding
minimum=25 # Минимальное количество роутеров с Ygg
timestart=$(date '+%Y-%m-%d %H:%M:%S')
###

# Проверка рабочих директорий:
echo -n $netdb...
cd $netdb &> /dev/null
if [[ $? != 0 ]]; then
	echo "X"
	exit 1
else
	echo "OK"
fi
ls

echo -n $outdb...
cd $outdb &> /dev/null
if [[ $? != 0 ]]; then
	echo "X"
	exit 2
else
	echo "OK"
fi
ls

# Очистка выходной директории
echo "Clearing the output directory..."
rm -r $outdb/* &> /dev/null

maketemp () { # Создание временной папки первичной сортировки
    echo "Creating temp directory..."
    rm -r $temp &> /dev/null
    mkdir $temp &> /dev/null
    if [[ $? != 0 ]]; then
        echo "Error. Exiting."
        exit 3
    fi
}
maketemp

copy () { # Копирование базы роутера в первичную временную папку
	echo "Copying the router base to the temp directory..."
	cp -r $netdb/* $temp/ &> /dev/null
	if [[ $? != 0 ]]; then
		echo "Error. Exiting."
		exit 4
	fi
}
copy

# Main section

echo "Finding the Yggdrasil routers:"
cd $temp
yggaddr=0
count=1

for((;;)); do # Поиск Yggdrasil-роутеров и их копирование в выходную директорию
    dir=$(ls -lh | head -n 2 | tail -n 1 | grep -o r.$)
    if [[ $? != 0 ]]; then
        break
    fi

    cd $dir
    for((;;)); do
        dat=$(ls -lh | head -n 2 | tail -n 1 | grep -E -w -o routerInfo.*.dat$)
        if [[ $? != 0 ]]; then # Если файлов в папке не осталось, выходим и удаляем ее
            cd $temp
            rmdir $dir
            break
        fi

        echo -n "[$count] "
        echo -n "$dat ["
        cat $dat | grep '=.[23]..:' &> /dev/null # Поиск host=200: или host=300:

        if [[ $? == 0 ]]; then # Успех, забираем
            echo "+]"
            let yggaddr++
            mkdir $outdb/$dir &> /dev/null
            mv ./$dat $outdb/$dir
            echo $dat >> $success
        else # Не успех, удаляем
            echo ".]"
            rm ./$dat
        fi
        let count++
    done
done

echo -e "\n================================================= YGGDRASIL *"
cat $success
rm $success
echo -e   "==========================================================="

echo -e "Reseed building..."
yggvolume=$(($yggaddr / 100 * 70)) # 70% ресида - Ygg-роутеры.
echo -n "Need "
if [[ $yggvolume < $minimum ]]; then # Если их меньше minimum, докладываем 25 роутеров обычных
    echo -n "25 "
    paddingcount=25
else
    paddingcount=$(($yggaddr / 100 * 30))
    echo -n "$paddingcount "
fi
echo "regular routers"

cd $temp
maketemp
copy
echo -n "Padding status: "
realpadding=0
for((i=0; $i < $paddingcount; i++)); do

    rand=$(( $RANDOM % 10 ))
    for((j=0;$j!=$rand;j++)); do
        cd $temp
        dir=$(ls -lh | head -n 2 | tail -n 1 | grep -o r.$)
        if [[ $? != 0 ]]; then
            echo "Dir error! PADDING-RAND-FOR"
            exit 5
        fi
        cd $dir
        dat=$(ls -lh | head -n 2 | tail -n 1 | grep -E -w -o routerInfo.*.dat$)
        if [[ $? != 0 ]]; then # Если файлов в папке не осталось, выходим и удаляем ее
            cd $temp
            rmdir $dir
        else
            rm ./$dat
        fi
        cd $temp
    done

    padselect () { # Дополнение ресида случайными роутерами
        cd $temp
        dir=$(ls -lh | head -n 2 | tail -n 1 | grep -o r.$)
        if [[ $? != 0 ]]; then
                echo "."
                padselect
        fi
        cd $dir
        dat=$(ls -lh | head -n 2 | tail -n 1 | grep -E -w -o routerInfo.*.dat$)
        if [[ $? != 0 ]]; then # Если файлов в папке не осталось, выходим и удаляем ее
                cd $temp
                rmdir $dir
                padselect
        fi
    }
    padselect

    mkdir $outdb/$dir &> /dev/null
    mv ./$dat $outdb/$dir
    echo $dat >> $padding
    let realpadding++
    echo -n "*"
done

echo -e "\n=================================================== PADDING *"
cat $padding
rm $padding
echo -e   "==========================================================="
echo -e "\nstarted:  $timestart\nfinished: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "total routers: $count"
echo -e "reseed build:  $(($yggaddr+$realpadding)) ($yggaddr/$realpadding)\n"
echo -e "Yggdrasil I2P reseed creator | acetone, 2021\n"

# Update web page

sed -i "s/>[0-9]\{1,1000\}</>$yggaddr</" /srv/pyseeder/output/seed.html
echo "Web page updated"
