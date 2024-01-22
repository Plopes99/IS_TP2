import { Injectable } from '@nestjs/common';
import { PrismaClient } from "@prisma/client";

@Injectable()
export class PrismaService extends PrismaClient {
    constructor() {
        const postgresUrl = 'postgresql://is:is@db-rel:5432/is?schema=public';

        super({
            datasources: {
                db: {
                    url: postgresUrl,
                },
            },
        });
    }
}