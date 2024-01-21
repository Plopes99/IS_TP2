import { Body, Controller, Delete, Get, Param, Post, Put } from "@nestjs/common";
import { CountryDTO} from "../dto/countries.dto";
import { CountriesService } from "./countries.service";

@Controller('countries')
export class CountriesController {
    constructor(private countryService: CountriesService) {}

    @Get()
    async getCoutries(){
      return this.countryService.getCountries;
    }

    @Post()
    async createCountry(@Body() dto: CountryDTO){
    return this.countryService.createCountry(dto);
    }

    @Put(':id')
    async update(@Param('id') id: number, @Body() dto: CountryDTO){
      return  this.countryService.updateCountry(id, dto)
    }

    @Delete(':id')
    async delete(@Param('id') id: number){
      return this.countryService.deleteCountry(id)
    }

    @Get(":id")
    async getCountry(@Param('id') id:number){
      return this.countryService.getCountry(id)  
    }
}

