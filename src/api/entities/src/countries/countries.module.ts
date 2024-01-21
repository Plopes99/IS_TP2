import { Module } from '@nestjs/common';
import { CountriesController } from './countries.controller';
import { CountriesService } from './countries.service';

@Module({ 
    providers: [CountriesService],
    controllers: [CountriesController]
})

export class CountriesModule {}
