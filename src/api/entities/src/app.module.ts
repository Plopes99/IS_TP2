import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DisastersModule } from './disasters/disasters.module';
import { CountriesService } from './countries/countries.service';
import { CountriesController } from './countries/countries.controller';
import { CountriesModule } from './countries/countries.module';
import { CategoriesModule } from './categories/categories.module';
import { PrismaModule } from './prisma/prisma.module';
import { DisastersController } from './disasters/disasters.controller';
import { CategoriesController } from './categories/categories.controller';
import { DisastersService } from './disasters/disasters.service';
import { CategoriesService } from './categories/categories.service';

@Module({
  imports: [ DisastersModule, CountriesModule, CategoriesModule, PrismaModule],
  controllers: [AppController, CountriesController, DisastersController, CategoriesController],
  providers: [AppService, CountriesService, DisastersService, CategoriesService],
})
export class AppModule {}
