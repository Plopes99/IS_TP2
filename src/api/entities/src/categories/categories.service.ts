import { Injectable } from '@nestjs/common';
import { PrismaService } from "../prisma/prisma.service";
import { CategoriesDto } from "../dto/categories.dto";

@Injectable()
export class CategoriesService {
    constructor(private prisma: PrismaService) {}

    async getCategorys(){
        const categories = await this.prisma.category.findMany({
            select: {               
            categoryName: true,
            accidentsTypes: true,
            damageTypes: true,
            }
        })
        if (categories.length === 0) return { message: "Não foram encontrados Categorias"}
        return categories;
    }

    async createCategories(dto: CategoriesDto){
        try {
            return await this.prisma.category.create({
              data: {
                categoryName: dto.categoryName,
                accidentsTypes: dto.accidentsTypes,
                damageTypes: dto.damageTypes
                
              }
            })
          } catch (error){
            return {
              message: "Não foi possível concluir o pedido"
            }
          }

    }

    async deleteCategory (id: number){
        const categoryID = String(id);
        const categoryExist = await this.prisma.category.findUnique({
          where :{
            id: categoryID,
          },
        })
    
    
        try{
          return await this.prisma.category.delete({
            where:{id: categoryID}
          })
        }catch(error){
          return {
            message: "Não foi possível concluir o pedido"
          }
        }
      }


    async updateCategory(id: number, dto: CategoriesDto){
    const categoryID = String(id);
    const categoryExist = await this.prisma.category.findUnique({
        where :{
        id: categoryID,
        },
    })

    try{
        return await this.prisma.category.update({
        data: {
            categoryName: dto.categoryName,
            accidentsTypes: dto.accidentsTypes,
            damageTypes: dto.damageTypes
        },
        where:{
            id_category: categoryID,
        }
        });

    }catch(error){
        return {
        message: "Não foi possível concluir o pedido"
        }
    }
    }

    async getCategory(id: number){
    const categoryID = Number(id)

    try{
        return await this.prisma.category.findUnique({
        where :{
            id_category: categoryID,
        },
        })

    }catch(error){
        return {
        message: "Não foi possível concluir o pedido"
        }
    }

    }
}
