import { IsString, IsOptional, IsDate, IsNumber } from 'class-validator';

export class CountryDTO {
    @IsString()
    countryName?: string;
    

}