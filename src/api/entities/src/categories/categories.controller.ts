import { Body, Controller, Delete, Get, Param, Post, Put } from "@nestjs/common";
import { CategoriesDto } from "../dto/categories.dto";
import { CategoriesService } from "./categories.service";

@Controller('categories')
export class CategoriesController {
    constructor(private categoryService: CategoriesService) {}

    @Get()
    async getCategories(){
      return this.categoryService.getCategories();
    }

    @Post()
    async createCategory(@Body() dto: CategoriesDto){
    return this.categoryService.createCategories(dto);
    }

    @Put(':id')
    async update(@Param('id') id: number, @Body() dto: CategoriesDto){
      return  this.categoryService.updateCategory(id, dto)
    }

    @Delete(':id')
    async delete(@Param('id') id: number){
      return this.categoryService.deleteCategory(id)
    }

    @Get(":id")
    async getCategory(@Param('id') id:number){
      return this.categoryService.getCategory(id)  
    }
}
