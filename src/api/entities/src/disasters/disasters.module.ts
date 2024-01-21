import { Module } from '@nestjs/common';
import { DisastersController } from './disasters.controller';
import { DisastersService } from './disasters.service';

@Module({
  controllers: [DisastersController],
  providers: [DisastersService]
})
export class DisastersModule {}
