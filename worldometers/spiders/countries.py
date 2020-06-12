# -*- coding: utf-8 -*-
import scrapy

class CountriesSpider(scrapy.Spider):
    name = 'countries'
    allowed_domains = ['www.worldometers.info']
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']

    def parse(self, response):
        countries = response.xpath("//td/a")
        for country in countries:
            name = country.xpath(".//text()").get()
            link = country.xpath(".//@href").get()

            #absolute_url = f"https://www.worldometers.info{link}"
            #absolute_url = response.urljoin(link)
            
            yield response.follow(url=link, callback=self.parse_country, meta={'country_name': name})

    def parse_country(self, response):
        name = response.request.meta['country_name']
        rows = response.xpath("(//table[@class='table table-striped table-bordered table-hover table-condensed table-list'])[1]/tbody/tr")

        country_pop_list = list()
        census_year = None
        country_population = None

        for index, row in enumerate(rows):
            year = row.xpath(".//td[1]/text()").get()
            population = row.xpath(".//td[2]/strong/text()").get()

            census_year = year
            country_population = population

            if index > 1: #Stepping back an year would be good enough
                break

        # The last table contains the region level values
        # if there are no regions data captured justreturnthe value for the country
        country_region_rows = response.xpath("(//table[@class='table table-hover table-condensed table-list'])[1]/tbody/tr")

        if country_region_rows is None:

            self.logger.info('No region data found for %s', name)
            yield {
                'country_name': name,
                'census_year': year,
                'population':country_population
            }

        for country_region_row in country_region_rows:
            country_pop_dict = dict()
            region_name = country_region_row.xpath(".//td[2]/text()").get()
            region_population = country_region_row.xpath(".//td[3]/text()").get()

            country_pop_dict['country_name'] = name
            country_pop_dict['census_year'] = census_year
            country_pop_dict['country_population'] = country_population
            country_pop_dict['region_name'] = region_name
            country_pop_dict['region_population'] = region_population
            country_pop_list.append(country_pop_dict)

        for processed_row in country_pop_list:
            yield processed_row

