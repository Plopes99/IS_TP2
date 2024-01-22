import { Injectable } from '@nestjs/common';
import { PrismaService } from "../prisma/prisma.service";
import { DisasterDTO } from "../dto/disasters.dto";

@Injectable()
export class DisastersService {
    constructor(private prisma: PrismaService) { }

    async getDisasters() {
        const disasters = await this.prisma.disaster.findMany({
            select: {
                countryId: true,
                date: true,
                fatalities: true,
                operator: true,
                aircraftType: true
            }
        })
        if (disasters.length === 0) return { message: "Não foram encontrados Categorias!!" }
        return disasters;
    }

    async createDisasters(dto: DisasterDTO) {
        try {
            return await this.prisma.disaster.create({
                data: {
                    date: dto.date,
                    fatalities: dto.fatalities,
                    operator: dto.operator,
                    aircraftType: dto.aircraftType,
                    countryId: dto.countryId
                }
            })
        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido!"
            }
        }

    }

    async deleteDisaster(id: number) {
        const disasterID = String(id);
        const disasterExist = await this.prisma.disaster.findUnique({
            where: {
                id: disasterID,
            },
        })


        try {
            return await this.prisma.disaster.delete({
                where: { id: disasterID }
            })
        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }
    }


    async updateDisaster(id: number, dto: DisasterDTO) {
        const disasterID = String(id);
        const disasterExist = await this.prisma.disaster.findUnique({
            where: {
                id: disasterID,
            },
        })

        try {
            return await this.prisma.disaster.update({
                data: {
                    date: dto.date,
                    fatalities: dto.fatalities,
                    operator: dto.operator,
                    aircraftType: dto.aircraftType
                },
                where: {
                    id: disasterID,
                }
            });

        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }
    }

    async getDisaster(id: number) {
        const disasterID = String(id)

        try {
            return await this.prisma.disaster.findUnique({
                where: {
                    id: disasterID,
                },
            })

        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }

    }
}
