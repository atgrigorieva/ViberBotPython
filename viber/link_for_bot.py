import csv
import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin',
                                        password='5112274', host='78.24.216.107', port=5433)

with conn.cursor() as cursor:
    with open("article_all_4.csv") as f_obj:
        reader = csv.DictReader(f_obj, delimiter=';')
        for line in reader:
           #print(line["ИД"])
            cursor.execute("UPDATE products SET link = %s, image = %s WHERE id_site Like '%%#_%s' ESCAPE '#'", (line["Ссылка"], line["Картинка"], int(line["ИД"])))
            conn.commit()
            '''cursor.execute("SELECT id_product, articul, product, id_site, link, image FROM public.products WHERE id_site Like '%%#_%s' ESCAPE '#'", [int(line["ИД"])])
            output = cursor.fetchall()
            for row in output:
                print(row[1])'''
