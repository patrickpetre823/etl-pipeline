# etl-pipeline
Small project to learn basics of airflow and etl pipeline creation


1. Create folders and set uid
2. curl compose file
3. celeryworker to local
4. delete celery lines
5. load_examples = "false"
6. delete redis
7. delete worker
8. delete dependency of redis
9. comment out image and use costum build .
10. create dockerfile
11. fill dockerfile from airflow docs
12. delete the airflow version in it
13. create requirements
14. remove triggerer in compose
15. add .gitignore + api-key
16. add make_df
17. add retrieval time + pytz for timezone
18. add retrieval date
19. added DB
20. tretrieval time to europe/berlin time
21. DF COlumn Names: 'id', 'name', 'brand', 'street', 'place', 'lat', 'lng', 'dist', 'diesel', 'e5', 'e10', 'isOpen', 'houseNumber', 'postCode', 'retrieval_time', 'retrieval_date'
22. JSON:
{
    "ok": true,
    "license": "CC BY 4.0 -  https:\/\/creativecommons.tankerkoenig.de",
    "data": "MTS-K",
    "status": "ok",
    "stations": [
        {                                                     Datentyp, Bedeutung
            "id": "474e5046-deaf-4f9b-9a32-9797b778f047",   - UUID, eindeutige Tankstellen-ID
            "name": "TOTAL BERLIN",                         - String, Name
            "brand": "TOTAL",                               - String, Marke
            "street": "MARGARETE-SOMMER-STR.",              - String, Straße
            "place": "BERLIN",                              - String, Ort
            "lat": 52.53083,                                - float, geographische Breite
            "lng": 13.440946,                               - float, geographische Länge
            "dist": 1.1,                                    - float, Entfernung zum Suchstandort in km
            "diesel": 1.109,                                \
            "e5": 1.339,                                     - float, Spritpreise in Euro
            "e10": 1.319,                                   /
            "isOpen": true,                                 - boolean, true, wenn die Tanke zum Zeitpunkt der
                                                              Abfrage offen hat, sonst false
            "houseNumber": "2",                             - String, Hausnummer
            "postCode": 10407                               - integer, PLZ
        },
        ... weitere Tankstellen
    ]
}
23. Added XCom (carefull: airflow 2.0+ uses context not kwargs)
24. Google CLoud Migration
        create e2 instance (Ubunut, HTTPS possible)
        Generating ssh key manually -> ssh-keygen -t rsa -f ~/.ssh/FILENAME -C USERNAME
        adding public key to gcp
        connecting ssh username@external-ip-adress
        installing docker https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
25. cloning github repo to vm
26. adding user to github group: sudo usermod -aG docker $USER
27. starting docker compose
28. ERROR
29. Create another VM but more ram and cpu
30. Now works but task with database throws error, probabyl bc db is not nitialized
https://medium.com/@kwattrapuranjay/apache-airflow-on-google-cloud-vm-a-complete-guide-with-custom-mysql-database-redis-caching-and-c00d1fd86cf2
31. create sql instance in gcp + db
32. create service account "cloud SQL Client"
33. create another ssh key for ssh-remote connection inside of visual studio code
        ssh-keygen -t rsa -b 4096 -C "my-mail@deine-email.de" locally and then put inside gcp vm (probabyl first key has wrong name or something)
34. change owner of files to my user
        sudo chown -R patrickpetre823:patrickpetre823 /home/patrickpetre823/etl-pipeline/dags/


36. add git user and email to my config:
        git config --global user.name "Dein GitHub Anzeigename"
        git config --global user.email "Deine GitHub E-Mail"
37. add ssh. key on vm ssh-keygen -t ed25519 -C "deine_github_email@example.com" and insert public key into github gcp/ssh keys
38. change connection type from https to ssh
        git remote set-url origin git@github.com:patrickpetre823/etl-pipeline.git

36. Update DAG and clean up pycache)
37. Create VPC and activate service networking API
38. private IPs activated for SQL-DB
39. Create FW rule for sql db
40. install psql & tested connection with psql from vm



