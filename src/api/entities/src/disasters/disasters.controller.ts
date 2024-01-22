import { Body, Controller, Delete, Get, Param, Post, Put } from "@nestjs/common";
import { DisasterDTO } from "../dto/disasters.dto";
import { DisastersService } from "./disasters.service";
@Controller('disasters')
export class DisastersController {
    constructor(private disasterService: DisastersService) {}

    @Get()
    async getDisasters(){
      return this.disasterService.getDisasters();
    }

    @Post()
    async createDisaster(@Body() dto: DisasterDTO){
    return this.disasterService.createDisasters(dto);
    }

    @Put(':id')
    async update(@Param('id') id: number, @Body() dto: DisasterDTO){
      return  this.disasterService.updateDisaster(id, dto)
    }

    @Delete(':id')
    async delete(@Param('id') id: number){
      return this.disasterService.deleteDisaster(id)
    }

    @Get(":id")
    async getNoticia(@Param('id') id:number){
      return this.disasterService.getDisaster(id)  
    }

}
