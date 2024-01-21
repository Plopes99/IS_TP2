import { IsDate, IsOptional, IsString, IsNumber } from 'class-validator';

export class DisasterDTO {
  @IsString()
  date?: Date;

  @IsOptional()
  @IsString()
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