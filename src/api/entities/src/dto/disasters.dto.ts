import { IsDate, IsOptional, IsString, IsNumber } from 'class-validator';

export class DisasterDTO {
  @IsDate()
  date?: Date;

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

  @IsDate()
  createdOn?: Date;

  @IsDate()
  updatedOn?: Date;
}