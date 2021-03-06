import scrapy


class NewJerseySpider(scrapy.Spider):
    name = "new_jersey_hospital"
    start_urls = ['https://newjersey.mylicense.com/verification_4_6/Search.aspx?facility=Y']
    custom_settings ={
        'ROBOTSTXT_OBEY': False
    }
    # handle_httpstatus_list = [404]
    p = 0
    pages = []
    n = 0
    all_professions = []
    progress = 0
    last = 0
    type = 'Y'
    main_list = []

    def parse(self, response):
        professions = response.xpath('//*[@id="t_web_lookup__profession_name"]/option/@value').extract()
        self.all_professions = professions[::-1]
        profession = self.all_professions.pop()
        if profession != '':
            print(profession)
            yield scrapy.FormRequest(
                url='https://newjersey.mylicense.com/verification_4_6/Search.aspx?facility={}'.format(self.type),
                meta={
                    'type': type,
                    'last': 0,
                },
                formdata={
                    '__VIEWSTATE': response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                    '__VIEWSTATEGENERATOR': response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(default=''),
                    '__EVENTVALIDATION': response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(default=''),
                    't_web_lookup__profession_name': profession,
                    'sch_button': 'Search',

                },
                callback=self.pagination
            )
        else:
            profession = self.all_professions.pop()
            if profession != '':
                print(profession)
                yield scrapy.FormRequest(
                    url='https://newjersey.mylicense.com/verification_4_6/Search.aspx?facility={}'.format(self.type),
                    meta={
                        'type': type,
                        'last': 0,
                    },
                    formdata={
                        '__VIEWSTATE': response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                        '__VIEWSTATEGENERATOR': response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(
                            default=''),
                        '__EVENTVALIDATION': response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(
                            default=''),
                        't_web_lookup__profession_name': profession,
                        'sch_button': 'Search',
                    },
                    callback=self.pagination
                )

    def pagination(self, response):
        print("___pagination___")
        links = response.xpath('//*[@id="datagrid_results"]//td/a/@href').extract()
        last = response.meta.get('last')
        if links:
            len_links = len(links)
            print('------')
            if self.p == 0:
                urls = response.xpath('//a/@href').re("(datagrid_results\$_ctl44\$_ctl.+?)'")[::-1]
                urls_page = response.xpath('//a[contains(@href, "datagrid_results$_ctl44$_ctl")]/font/text()').extract()
                self.pages = urls
                # for q in urls:
                #     if q not in self.main_list:
                #         self.pages.append(q)
                new = []
                for u in urls_page:
                    if u not in self.main_list:
                        new.append(u)
                print(urls_page, len(urls_page))
                print('++++++++++++++++++++++++++++++++++++++++++++++++++')
                if len(new) != 40:
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++')
                    last = 1
                    self.main_list = []
                    try:
                        self.pages = urls[:-(40 - len(new))]
                    except:
                        pass
                self.main_list = self.main_list + urls_page
                print(self.pages)
                # print(urls_page)
            self.p += 1
            for link in links:
                yield scrapy.Request(
                    url='https://newjersey.mylicense.com/verification_4_6/{}'.format(link),
                    meta={
                        'len_links': len_links,
                        '__VIEWSTATE': response.xpath(
                            '//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                        '__VIEWSTATEGENERATOR': response.xpath(
                            '//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(default=''),
                        '__EVENTVALIDATION': response.xpath(
                            '//*[@id="__EVENTVALIDATION"]/@value').extract_first(default=''),
                        'type': response.meta.get('type'),
                        'last': last
                        # 'CurrentPageIndex': response.xpath(
                        #     '//*[@id="CurrentPageIndex"]/@value').extract_first(default=''),
                    },
                    dont_filter=True,
                    callback=self.parse_item
                )
        else:
            print('======================================================')

            self.p = 0
            # last = 1
            yield scrapy.Request(
                url='https://newjersey.mylicense.com/verification_4_6/Search.aspx?facility={}'.format(self.type),
                dont_filter=True,
                meta={
                    'last': last
                },
                callback=self.parse1
            )

    def parse1(self, response):
        print("************parse1*********")
        print(self.p)
        prof = self.all_professions.pop()
        print(prof)
        print(response.url)
        yield scrapy.FormRequest(
            url='https://newjersey.mylicense.com/verification_4_6/Search.aspx?',
            meta={
                'type': self.type,
                'last': 0
            },
            formdata={
                '__VIEWSTATE': response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(default=''),
                '__VIEWSTATEGENERATOR': response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(default=''),
                '__EVENTVALIDATION': response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(default=''),
                't_web_lookup__profession_name': prof,
                'sch_button': 'Search',
            },
            dont_filter=True,
            callback=self.pagination
        )

    def parse_item(self, response):
        self.n += 1
        if response.status != 404:
            i = {}
            if response.meta.get('type') == 'Y':
                i['Type'] = 'doctor'
            else:
                i['Type'] = 'hospital'
            i['Name'] = response.xpath('//*[@id="full_name"]/text()').extract_first(default='')
            i['Profession/License Type'] = response.xpath('//*[@id="profession_id"]/text()').extract_first(default='')
            i['License No'] = response.xpath('//*[@id="license_no"]/text()').extract_first(default='')
            i['License Status'] = response.xpath('//*[@id="sec_lic_status"]/text()').extract_first(default='')
            i['Status Change Reason'] = response.xpath('//*[@id="changeReason"]/text()').extract_first(default='')
            i['Issue Date'] = response.xpath('//*[@id="issue"]/text()').extract_first(default='')
            i['Expiration Date'] = response.xpath('//*[@id="expiration_date"]/text()').extract_first(default='')
            i['Address'] = ''.join(response.xpath('//*[@id="Label_addr_city"]/../span[position()>1]/text()').extract())
            yield i
        mister_x = ''
        if self.n == response.meta['len_links']:
            self.n = 0
            if len(self.pages) != 0:
                mister_x = self.pages.pop()
            if response.meta.get('last') == 1 and len(self.pages) == 0:
                self.p = 0
                last = 0
                print("************len(self.pages) == 0*********")
                yield scrapy.Request(
                    url='https://newjersey.mylicense.com/verification_4_6/Search.aspx?facility={}'.format(self.type),
                    dont_filter=True,
                    meta={
                        'last': last
                    },
                    callback=self.parse1
                )
            else:
                if len(self.pages) == 0:
                    self.p = 0
                yield scrapy.FormRequest(
                    url='https://newjersey.mylicense.com/verification_4_6/SearchResults.aspx',
                    meta={
                        'type': type,
                        'last': response.meta.get('last')
                    },
                    formdata={
                        '__VIEWSTATE': response.meta.get('__VIEWSTATE'),
                        '__VIEWSTATEGENERATOR': response.meta.get('__VIEWSTATEGENERATOR'),
                        '__EVENTVALIDATION': response.meta.get('__EVENTVALIDATION'),
                        # 'CurrentPageIndex': response.xpath(
                        #     '//*[@id="CurrentPageIndex"]/@value').extract_first(default=''),
                        '__EVENTTARGET': mister_x,
                    },
                    dont_filter=True,
                    callback=self.pagination
                )

                self.progress += 1
                print('******************', self.progress, '***************')
                print('******************', mister_x, '***************')



