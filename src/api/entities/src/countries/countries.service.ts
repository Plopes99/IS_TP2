import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CountryDTO } from '../dto/countries.dto';


@Injectable()
export class CountriesService {
    constructor(private prisma: PrismaService) { }

    async getCountries() {
        const country = await this.prisma.country.findMany({
            select: {
                countryName: true,
            }
        })
        if (country.length === 0) return { message: "Não foram encontrados Países" }
        return country;
    }

    async createCountry(dto: CountryDTO) {
        try {
            return await this.prisma.country.create({
                data: {
                    countryName: dto.countryName
                }
            })
        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }

    }

    async deleteCountry(id: number) {
        const coutryID = String(id);
        const countryExist = await this.prisma.country.findUnique({
            where: {
                id: coutryID,
            },
        })

        try {
            return await this.prisma.country.delete({
                where: { id: coutryID }
            })
        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }
    }


    async updateCountry(id: number, dto: CountryDTO) {
        const countryID = String(id);
        const noticiaExist = await this.prisma.country.findUnique({
            where: {
                id: countryID,
            },
        })

        try {
            return await this.prisma.country.update({
                data: {
                    countryName: dto.countryName
                },
                where: {
                    id: countryID,
                }
            });

        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }
    }

    async getCountry(id: number) {
        const countryID = String(id)

        try {
            return await this.prisma.country.findUnique({
                where: {
                    id: countryID,
                },
            })

        } catch (error) {
            return {
                message: "Não foi possível concluir o pedido"
            }
        }

    }
}
