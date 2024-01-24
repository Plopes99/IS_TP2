import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'TP2 - IS Desastres Aéreos';
  }
}
