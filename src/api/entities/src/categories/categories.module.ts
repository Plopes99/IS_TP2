import { Module } from '@nestjs/common';
import { CategoriesController } from './categories.controller';
import { CategoriesService } from './categories.service';
import {ConfigModule} from "@nestjs/config";
import {PrismaModule} from "../prisma/prisma.module"

@Module({
  imports: [ConfigModule, PrismaModule],
  controllers: [CategoriesController],
  providers: [CategoriesService]
})
export class CategoriesModule {}
