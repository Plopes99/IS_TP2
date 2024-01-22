import { Module } from '@nestjs/common';
import { CountriesController } from './countries.controller';
import { CountriesService } from './countries.service';
import {ConfigModule} from "@nestjs/config";
import {PrismaModule} from "../prisma/prisma.module"

@Module({ 
    imports: [ConfigModule, PrismaModule],
    providers: [CountriesService],
    controllers: [CountriesController]
})

export class CountriesModule {}
