# -*- coding: utf-8 -*-
import unicodecsv
from lxml import html
from retrying import retry
import re


@retry(wait_random_min=5000, wait_random_max=10000)
def scrape_thread(thread):
    t = html.parse(thread+"&action=printpage;")
    for br in t.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    title = t.xpath('//dt[@class="postheader"]/strong/text()')[0]
    posts = zip(t.xpath('//dt[@class="postheader"]'), t.xpath('//dd[@class="postbody"]'))
    qid = re.findall(r'topic=(\d*)', thread)[0]
    posters = set()
    inferred_replies = set()
    for i, post in enumerate(posts):
        poster = post[0].xpath('./strong[2]/text()')[0]
        date = post[0].xpath('./strong[3]/text()')[0]
        content = post[1].text_content().strip()
        local_id = i-1
        unique_id = qid+"_top" if local_id < 0 else qid + "_" + str(local_id)
        reply_to = qid+"_top" if local_id >= 0 else " "
        for p in posters:
            if p in content:
                inferred_replies.add(p)
        w.writerow([unique_id, qid, local_id, title, poster, date, reply_to, content, ' '.join(inferred_replies), subforum])
        f.flush()
    posters.add(poster)

page = html.parse("http://sjogrensworld.org/forums/index.php")
f = open('sjogrens.csv', 'w')
w = unicodecsv.writer(f, encoding='utf-8', lineterminator='\n')
w.writerow(['uniqueID', 'qid', 'localID', 'title', 'poster', 'date', 'replyTo', 'content', 'infered_replies', 'group'],)
for forum in page.xpath('//td[@class="info"]/a'):
    subforum = forum.text
    forum_page = html.parse(forum.attrib['href'])
    while True:
        for thread in forum_page.xpath('//td[contains(@class, "subject")]//span/a'):
            print thread.attrib['href'], thread.text
            scrape_thread(thread.attrib['href'])
        next_page = forum_page.xpath('//div[@class="pagelinks"]/strong/following-sibling::a[1]')
        if next_page:
            forum_page = html.parse(next_page[0].attrib['href'])
        else:
            break
