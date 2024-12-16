FROM --platform=linux/x86_64 mysql:8.0.35-debian

ENV TZ=Asia/Tokyo
COPY ./init/* /docker-entrypoint-initdb.d/

COPY my.conf /etc/mysql/conf.d/my.conf

CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci", "--default-authentication-plugin=mysql_native_password", "--innodb-use-native-aio=0"]
