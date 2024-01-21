import { Module } from '@nestjs/common';
import { DisastersController } from './disasters.controller';
import { DisastersService } from './disasters.service';
import { PrismaService } from "../prisma/prisma.service";
import {ConfigModule} from "@nestjs/config"
import {PrismaModule} from "../prisma/prisma.module"

@Module({
  imports: [ConfigModule, PrismaModule],
  providers: [PrismaService,DisastersService],
  controllers: [DisastersController]
})
export class DisastersModule {}
