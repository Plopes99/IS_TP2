import { IsDate, IsOptional, IsString, IsNumber, IsJSON } from 'class-validator';

export class DisasterDTO {
  @IsString()
  date?: Date;

  @IsOptional()
  @IsJSON()
  geom?: any;

  @IsString()
  aircraftType?: string;

  @IsString()
  operator?: string;

  @IsNumber()
  fatalities?: number;

  @IsString()
  countryId?: string;
}