import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TeachersModule } from './teachers/teachers.module';
import { DisastersModule } from './disasters/disasters.module';
import { CountriesService } from './countries/countries.service';
import { CountriesController } from './countries/countries.controller';
import { CountriesModule } from './countries/countries.module';
import { CategoriesModule } from './categories/categories.module';
import { PrismaModule } from './prisma/prisma.module';

@Module({
  imports: [TeachersModule, DisastersModule, CountriesModule, CategoriesModule, PrismaModule],
  controllers: [AppController, CountriesController],
  providers: [AppService, CountriesService],
})
export class AppModule {}
