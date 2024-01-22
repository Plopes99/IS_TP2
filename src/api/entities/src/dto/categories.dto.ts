import { IsNotEmpty, IsNumber, IsOptional, IsString } from "class-validator";

// dto é como uma replica da tabela da base de dados, mas apenas com os dados que precisamos
// como este dto é para criar um novo categoria, não precisamos por exemplo do id, que é automaticamente atribuido pela db
export class CategoriesDto {
    @IsString()
    categoryName?: string;
  
    @IsString()
    accidentsTypes?: string;
  
    @IsString()
    damageTypes?: string;
  
    
}
