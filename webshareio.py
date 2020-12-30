# In case you intend trying out proxies from WEBSHARE.IO
# Please note that the proxies, when downloaded, do not come
# in the format that python Scrapy uses and validates them
#
# Eg. WEBSHARE.IO proxy looks like
# 45.142.28.91:80:aqdrltbv-dest:xtqf1hocpf2d

# Scrapy needs them to look like
# http://<username>:<password>>@IPaddress:80


with open('path-to-txt-proxy-file-from-webshare.io', 'r') as proxy_file:
    with open('webshareproxies.txt', 'w') as p:
        for each in proxy_file.readlines():
            sep = each.split(':')
            port = ':'.join(sep[0:2])

            domain = f'http://{sep[2]}:{sep[3]}'.strip()
            proxy = f'{domain}@{port}\n'

            p.write(proxy)


# RUN python webshareio.py

# this reformats and writes the new modified version to a new file
# move this new file to the scrapy project you want to use it with
# for instance, amazon/amazoncrawl/proxies/the-file

