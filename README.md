# Marketing Bot
A bot to analyze the tweets with various & flexible configuration.

This project is based on this boilerplate(https://github.com/salimane/flask-mvc)

## Dependencies :

- if you have old version of project: 
```bash
pip uninstall -r requirements.txt
```

- To install the dependencies:
```bash
pip install -r requirements.txt
```

- To run:

```bash
python wsgi.py
```

### Notes

- Windows
mysqlclient

- [Empty Log File](https://www.tecmint.com/empty-delete-file-content-linux/)
```bash
du -sh main.log
> main.Log
du -sh main.log
```

- [See live Log on Ubuntu](https://superuser.com/questions/316578/how-can-i-view-live-logs-on-a-linux-server-ubuntu)
```bash
tail -f main.log
```

- Check MySQL Process LIST

```mysql
SHOW FULL PROCESSLIST
show variables like '%timeout%';
SET GLOBAL wait_timeout=30;

```

- Error 'The client was disconnected by the server because of inactivity. See wait_timeout and interactive_timeout for configuring this behavior.'
fixed by [How do I set wait_timeout to unlnmited in msyql?](https://askubuntu.com/a/892859/1083662)

update mysql config and restart the mysql service.

```
[mysqld]
wait_timeout = 31536000
interactive_timeout = 31536000
```

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql.service
```

# Database
## Tweet
### tweeted

0: none <br/>
1: retweet <br/>
2: post <br/>

## Twitter Libraries
### [Tweepy](https://pypi.org/project/tweepy)

[Github](https://github.com/tweepy/tweepy)

- Fork 3.5k
- Start 7.8k
- watch 274
- latest version Dec 26, 2020
- Used By 2.59k
- Contributors: 187
- [Document](https://docs.tweepy.org/en/stable/index.html)

### [twitter](https://pypi.org/project/twitter)

[Github](https://github.com/python-twitter-tools/twitter)

- Fork 547
- Star 2.6k
- watch 159
- latest version: Jun 19, 2021
- used by 2.9k
- contributors: 64


### [python-twitter](https://pypi.org/project/python-twitter)

[Github](https://github.com/bear/python-twitter)
[APIs](https://github.com/sns-sdks/python-twitter/blob/master/pytwitter/api.py#L649)
- Fork: 960
- Star: 3.2k
- watch: 174
- Latest Version: Sep 30, 2018
- Used by: 5.5k
- Contributors: 133

## Reference

- [flask upload file get file path](https://www.codegrepper.com/code-examples/python/flask+upload+file+get+file+path)

## Others

- Media Ids
1418847104844304389
1418858925366054912

