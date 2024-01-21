import { Injectable } from '@nestjs/common';
import { PrismaClient } from "@prisma/client";
import { ConfigService } from "@nestjs/config"

@Injectable()
export class PrismaService extends PrismaClient {
    constructor(config: ConfigService) {
        super({
        datasources: {
            db: {
            url: config.get('postgresql://is:is@localhost:10002/is?schema=public')
            }
        }
        });
    }
}
